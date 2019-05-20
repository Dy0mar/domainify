# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import (
    Http404,
    JsonResponse
)
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from domains.models import DomainConfirmUpdate, Domain
from domains.views import messenger_proxy
from users.forms import UserChangeForm, UserForm
from users.models import Settings, User
from users.utils import reverse_value, get_notification_list
from users.tasks import send_xmppp_message, send_mail_to_user


@method_decorator(permission_required('is_superuser'), name='dispatch')
class UserListView(ListView):
    template_name = 'users/user_list.html'
    context_object_name = 'user_list'
    model = User
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'user_list'
        context['next_url'] = reverse('user-list')

        return context


@permission_required('is_superuser')
def change_user_status(request):
    if request.is_ajax():
        pk = request.GET.get('id')
        name = request.GET.get('name')
        try:
            assert pk
            assert hasattr(User, name)
            user = User.objects.get(pk=pk)
        except (AssertionError, User.DoesNotExist):
            return JsonResponse({}, status=404)

        # Запретить снятие is_superuser разрешить is_staff
        if user == request.user and name not in ('is_staff',):  # allowed change
            return JsonResponse(
                {'msg': 'Нельзя так просто взять и снять с себя админа. '
                        'Попроси другого админа сделать сие действие'
                 },
                safe=False, status=200
            )

        if name == 'is_active':
            user.is_active = reverse_value(user.is_active)
        if name == 'is_staff':
            user.is_staff = reverse_value(user.is_staff)
        if name == 'is_superuser':
            user.is_superuser = reverse_value(user.is_superuser)
        user.save()
        return JsonResponse({}, status=200)
    raise Http404


@permission_required('is_superuser')
def user_add(request):
    form = UserChangeForm(data=request.POST.copy() or None)

    if form.is_valid():
        if form.has_changed():
            form.save()
        return redirect('user-list')
    return render(request, 'users/user_add_edit.html', {
        'form': form,
        'created': True
    })


@login_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)

    data = request.POST.copy()
    next_url = request.GET.get('next_url')

    form = UserForm(
        data=data or None,
        current_user=request.user,
        instance=user
    )
    if form.is_valid():
        next_url = data.get('next_url')
        if form.has_changed():
            form.save()
        if next_url == reverse('user-list'):
            return redirect('user-list')
        else:
            return redirect('user-profile')

    return render(request, 'users/user_add_edit.html', {
        'form': form,
        'next': next_url
    })


@permission_required('is_superuser')
def user_delete(request, pk):
    if request.is_ajax():
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return JsonResponse({}, status=404)

        if request.user == user:
            return JsonResponse({
                'msg': 'Нельзя так просто взять и удалить себя ;)'
            }, safe=False, status=200)
        user.delete()
        return JsonResponse({}, status=200)
    raise Http404


@login_required
def user_info(request):
    context = {}
    user = request.user
    s = user.user_settings.first()

    if user.is_staff_or_admin:
        context = {
            'user': user,
            'settings': s
        }

        qs = User.objects.all()
        if user.is_superuser:

            if s:
                context['notification_list'] = get_notification_list(
                    s.user_notification_list
                )

            context['admin_list'] = qs.filter(
                is_superuser=True
            ).exclude(id=user.pk)

        elif user.is_staff:

            if s:
                context['notification_list'] = get_notification_list(
                    s.user_notification_list
                )

            context['manager_list'] = qs.filter(
                is_superuser=False,
                is_staff=True
            ).exclude(id=user.pk)

    context.update({
        'domain_registrar': user.has_group_perm('can_manage_domain_registrar'),
        'editor_site': user.has_group_perm('can_edit_site'),
        'alexa_traffic': user.has_group_perm('can_manage_alexa_traffic'),
    })
    return render(request, 'users/user_profile.html', context)


@login_required
def change_notification_list(request):
    """
    Получать уведомления, приходящие к другим админам.
    Добавить или удалить админа в список получателей.

    """
    if request.is_ajax() and request.user.is_staff_or_admin:
        pk = request.GET.get('id')
        try:
            assert pk
            user = User.objects.get(pk=pk)
        except (AssertionError, User.DoesNotExist):
            return JsonResponse({}, status=404)

        # Запретить снятие уведомлений
        if user == request.user:
            return JsonResponse(
                {'msg': 'Нельзя так просто взять и не получать уведомления!'},
                safe=False, status=200
            )

        s, created = Settings.objects.get_or_create(
            user=request.user
        )

        notification_list = get_notification_list(
            s.user_notification_list
        )

        if user.pk in notification_list:
            notification_list.remove(user.pk)
        else:
            notification_list.append(user.pk)

        new_notification = ','.join([str(x) for x in notification_list])

        s.user_notification_list = new_notification
        s.save()

        return JsonResponse({}, status=200)
    raise Http404


@login_required
def change_notification_method(request):
    if request.is_ajax():
        param = request.GET.get('name')
        if param not in ('email', 'pidgin'):
            return JsonResponse({}, status=403)

        s, created = Settings.objects.get_or_create(
            user=request.user,
        )
        if param == 'email':
            s.email = reverse_value(s.email)

        if param == 'pidgin':
            s.pidgin = reverse_value(s.pidgin)

        s.save()
        return JsonResponse({}, status=200)

    raise Http404


@login_required
def check_notification_method(request):
    if request.is_ajax():
        check_method = request.GET.get('check_method')

        if check_method not in ('email', 'pidgin'):
            return JsonResponse({'msg': 'Check ¯\\_(ツ)_/¯'}, safe=False)

        msg = ''

        if check_method == 'email':
            subject = 'Domainify BOT - Проверка почты'
            message = 'Если вы читаете это письмо, значит все хорошо )'
            from_email = settings.EMAIL_HOST_USER

            send_mail_to_user.apply_async(
                (subject, message, from_email, [request.user.email])
            )
            msg = 'Check your {}'.format(request.user.email)

        if check_method == 'pidgin':
            if request.user.pidgin:
                send_xmppp_message.apply_async(
                    (request.user.pidgin, 'Check ok =]')
                )
                msg = 'Check your {}'.format(request.user.pidgin)
            else:
                msg = 'Pidgin empty {}'.format(request.user.pidgin)

        return JsonResponse({'msg': msg}, safe=False)

    raise Http404


def confirm_up_done(request):
    registrar_perms = request.user.has_group_perm('can_manage_domain_registrar')
    editor_perms = request.user.has_group_perm('can_edit_site')
    if not any([registrar_perms or editor_perms]):
        raise PermissionDenied

    domain_name = request.GET.get('domain')
    confirm = request.GET.get('confirm')
    if confirm not in ('editor', 'redirect', 'status'):
        messages.error(request, 'Error - не задан параметр подтверждения')
        return redirect('notify')

    qs = DomainConfirmUpdate.objects.filter(
        domain__name=domain_name,
        done=False
    )
    if confirm == 'redirect':
        qs = qs.filter(new_data__contains='redirect')

    if confirm == 'editor':
        qs = qs.filter(new_data__contains='editor_method')

    notify_msg = 'Вы никогда не должны были получить это сообщение. ' \
                 'Уведомьте пожалуйста разработчика roman или betty'

    complete_notify = []

    for confirm_up in qs:
        confirm_up.done = True

        if confirm == 'redirect':
            notify_msg = '{}, {} подтвердил изменение редиректа с {} на {}'
            notify_msg = notify_msg.format(
                confirm_up.domain.name, confirm_up.responsible_admin,
                confirm_up.old_data.get('redirect'),
                confirm_up.new_data.get('redirect')
            )
        if confirm == 'editor':
            notify_msg = '{}, {} подтвердил изменение на сайте'.format(
                confirm_up.domain.name, confirm_up.responsible_admin,
            )

        if confirm == 'status':
            status = confirm_up.new_data.get('status')
            if status:
                try:
                    status = dict(Domain.CHOICE_STATUS)[
                        (status.replace('REQUIRES_', ''))]
                    domain = Domain.objects.get(name=domain_name)
                    domain.status = status
                    domain.save()
                except (KeyError, Domain.DoesNotExist):
                    messages.error(
                        request, 'Что-то пошло не так, либо значение '
                                 'status неверное либо домена не существует')
                    return redirect('notify')
            notify_msg = '{}, {} подтвердил статус'.format(
                confirm_up.domain.name, confirm_up.responsible_admin,
            )

        confirm_up.save()

        # уведомить менеджера домена | его может и не быть
        send_list = [confirm_up.domain.manager]

        # уведомить того, кто отредактировал данные
        if confirm_up.domain.manager != confirm_up.user_changed:
            send_list.append(confirm_up.user_changed)

        # если есть другие админы, уведомить и их
        if request.user != confirm_up.responsible_admin:
            send_list.append(confirm_up.responsible_admin)

        for user in send_list:
            # не отправлять повторяющихся юзеров
            if not user or user in complete_notify:
                continue

            messenger_proxy(request, user, notify_msg)
            complete_notify.append(user)

    return redirect('notify')


@login_required
def notify(request):
    user = request.user
    context = {}
    # group can_manage_domain_registrar
    if user.has_group_perm('can_manage_domain_registrar'):
        qs = DomainConfirmUpdate.objects.filter(
            responsible_admin=user,
            done=False,
        ).prefetch_related('domain__manager', 'user_changed')

        context['redirects'] = [
            x for x in qs.filter(new_data__contains='redirect')
        ]

        context['statuses'] = [
            x for x in qs.filter(new_data__contains='status')
        ]

    # group can_edit_site
    if user.has_group_perm('can_edit_site'):
        qs = DomainConfirmUpdate.objects.filter(
            responsible_admin=user,
            done=False,
        ).prefetch_related('domain')

        context['edits'] = qs

    # обновление уведомлений
    if request.is_ajax():
        cache_key = 'notify_count'
        notify_count = cache.get(cache_key)
        if notify_count is None:
            notify_count = 0
            for field in ('redirects', 'statuses', 'edits'):
                values = context.get(field)
                if values:
                    notify_count += len(values)
            cache.set(cache_key, notify_count, 60*5)
        return JsonResponse({'count': notify_count}, safe=False)

    return render(request, 'users/user_notify.html', context)
