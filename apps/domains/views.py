# -*- coding: utf-8 -*-
import csv

import whois
import datetime

from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test
)
from django.contrib.auth.models import User
from django.core import paginator
from django.db.models import Q
from django.http import (
    HttpResponseNotFound, HttpResponse, Http404, JsonResponse
)
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from domains.forms import DomainChangeForm, DomainFilterForm, DomainImportForm
from domains.models import Domain, ActionLog
from domains.utils import to_date, validate_small_date, validate_big_date
from users.views import check_staff_or_admin

DATE_NOTIFICATION = timezone.now() + datetime.timedelta(days=30)


def reverse_value(x):
    return False if x else True


def get_notifications(user):
    """
        return queryset notifications
    """
    qs = Domain.objects.none()

    if not user.is_superuser and not user.is_staff:
        return None

    if user.is_superuser:
        # count expiration
        qs = Domain.objects.filter(
            admin=user,
            date_expire__lte=DATE_NOTIFICATION
        )

    if user.is_staff:
        # count unread log-messages
        qs = Domain.objects.filter(
            manager=user,
            actionlog__is_read=False
        )
    return qs


@login_required
def domain_list(request, reminders='', my_list=False):
    current_page = 'domain_list'
    data = request.GET.copy()
    form = DomainFilterForm(data=data or None)
    qs = Domain.objects.all()
    if my_list:
        current_page = 'my_list'
        if request.user.is_superuser:
            qs = qs.filter(admin=request.user)
        elif request.user.is_staff:
            qs = qs.filter(manager=request.user)

    if reminders == 'admin':
        current_page = 'reminders'
        qs = qs.filter(date_expire__lte=DATE_NOTIFICATION)

    # reminders
    notification = get_notifications(request.user)

    data_filters = dict()

    if request.is_ajax():
        if not form.is_valid():
            return JsonResponse(data={}, status=404)

        # filters
        # domain name
        try:
            domain_name = data.get('domain-name')
            assert domain_name
            domain_name = domain_name.strip()
            qs = qs.filter(name__icontains=domain_name)
            data_filters['domain_name'] = domain_name
        except (AssertionError, IndexError, AttributeError):
            pass

        # company name
        try:
            company_name = data.get('company-name')
            assert company_name
            company_name = company_name.strip()
            qs = qs.filter(company_name__icontains=company_name)
            data_filters['company_name'] = company_name
        except (AssertionError, IndexError, AttributeError):
            pass

        # telephone
        try:
            telephone = data.get('telephone')
            assert telephone
            telephone = telephone.strip()
            qs = qs.filter(
                Q(telephone__icontains=telephone) |
                Q(telephone2__icontains=telephone) |
                Q(telephone3__icontains=telephone)
            )
            data_filters['telephone'] = telephone
        except (AssertionError, IndexError, AttributeError):
            pass

        # managers
        try:
            managers = data.getlist('managers')
            assert managers
            if 'None' in managers:
                managers.remove('None')
                qs = qs.filter(
                    Q(manager__pk__in=managers) | Q(manager__isnull=True)
                )
            else:
                qs = qs.filter(manager__pk__in=managers)
            data_filters['managers'] = User.objects.filter(pk__in=managers)
        except AssertionError:
            pass

        # admins
        try:
            admins = data.getlist('admins')
            assert admins
            if 'None' in admins:
                admins.remove('None')
                qs = qs.filter(
                    Q(admin__pk__in=admins) | Q(admin__isnull=True)
                )
            else:
                qs = qs.filter(admin__pk__in=admins)
            data_filters['admins'] = User.objects.filter(pk__in=admins)
        except AssertionError:
            pass

        # date registration
        date_registration_from = to_date(data.get('date_register_from'))
        date_registration_till = to_date(data.get('date_register_till'))
        if validate_small_date(date_registration_from,
                               date_registration_till):
            qs = qs.filter(date_register__gte=date_registration_from)
            data_filters['date_registration_from'] = date_registration_from

        if validate_big_date(date_registration_from,
                             date_registration_till) or date_registration_till:
            qs = qs.filter(date_register__lte=date_registration_till)
            data_filters['date_registration_till'] = date_registration_till

        # date request
        date_reguest = to_date(data.get('date_request'))
        try:
            assert date_reguest
            qs = qs.filter(date_register=date_reguest)
        except AssertionError:
            pass

        # date expiration
        date_expire_from = to_date(data.get('date_expire_from'))
        date_expire_till = to_date(data.get('date_expire_till'))
        if validate_small_date(date_expire_from,
                               date_expire_till):
            qs = qs.filter(date_expire__gte=date_expire_from)
            data_filters['date_expire_from'] = date_expire_from

        if validate_big_date(date_expire_from,
                             date_expire_till) or date_expire_till:
            qs = qs.filter(date_expire__lte=date_expire_till)
            data_filters['date_expire_till'] = date_expire_till

        # pci scan
        try:
            pci_scan = data.get('pci_scan')
            assert (pci_scan in ('0', '1'))
            pci_scan = int(pci_scan)
            if pci_scan == 1:
                qs = qs.filter(date_last_scan__isnull=False)
            if pci_scan == 0:
                qs = qs.filter(date_last_scan__isnull=True)
            data_filters['checks_pci'] = dict(
                DomainFilterForm.NULL_CHOICES)[pci_scan]
        except AssertionError:
            pass

        # status
        try:
            status = data.get('status')
            assert status in dict(Domain.CHOICE_STATUS).keys()
            qs = qs.filter(status=status)
            data_filters['status'] = status
        except AssertionError:
            pass

        domains_paginator = paginator.Paginator(qs, 50)

        try:
            page = int(data.get('page', '1'))
        except ValueError:
            page = 1

        try:
            domains = domains_paginator.page(page)
        except (paginator.EmptyPage, paginator.InvalidPage):
            domains = domains_paginator.page(domains_paginator.num_pages)

        return render(request, 'domains/inc/table.html', {
            'domain_list': domains,
            'data_filters': data_filters,
            'notification': notification,
            'form': form,
        })

    domains_paginator = paginator.Paginator(qs, 50)

    try:
        page = int(data.get('page', '1'))
    except ValueError:
        page = 1

    try:
        domains = domains_paginator.page(page)
    except (paginator.EmptyPage, paginator.InvalidPage):
        domains = domains_paginator.page(domains_paginator.num_pages)

    return render(request, 'domains/domain_list.html', {
        'domain_list': domains,
        'object_list': domains,
        'page_obj': domains,
        'form': form,
        'notification': notification,
        'current_page': current_page
    })


@login_required
@user_passes_test(check_staff_or_admin)
def domain_detail(request, pk):
    domain = get_object_or_404(Domain, pk=pk)
    return render(request, 'domains/domain_detail.html', {
        'domain': domain,
        'current_page': 'domain_detail'
    })


@login_required
@user_passes_test(check_staff_or_admin)
def domain_add_edit(request, pk=None):
    domain = None
    if pk:
        domain = get_object_or_404(Domain, pk=pk)

    data = request.POST.copy()
    form = DomainChangeForm(data=data or None, instance=domain)

    if form.is_valid() and form.has_changed():
        data = dict()

        if domain:
            action = ActionLog.EDIT_DOMAIN
            old_domain = Domain.objects.get(pk=pk)
            # list
            for field in form.changed_data:
                old = getattr(old_domain, field)
                new = form.cleaned_data[field]
                if field == 'manager':
                    old = old.pk
                    new = new.pk

                data['old_' + field] = old
                data[field] = new
        else:
            action = ActionLog.ADD_DOMAIN
            data = None

        log = ActionLog.objects.create(
            action=action,
            user=request.user,
            data=data,
            domain=domain
        )

        if domain and request.user == domain.manager:
            log.is_read = True
            log.save()

        form.save()
        return redirect('domain-detail', pk=domain.pk)

    return render(request, 'domains/domain_add_edit.html', {
        'form': form,
        'domain': domain,
        'current_page': 'domain_add' if not pk else ''
    })


@login_required
@user_passes_test(check_staff_or_admin)
def domain_logs(request, pk):
    domain = get_object_or_404(Domain, pk=pk)
    actions = domain.actionlog_set.all()

    return render(request, 'domains/domain_log_list.html', {
        'actions': actions,
        'domain': domain,
    })


@login_required
@permission_required('is_superuser')
def change_user_status(request):
    if request.is_ajax():
        pk = request.GET.get('id')
        name = request.GET.get('name')
        try:
            assert pk
            hasattr(Domain, name)
            user = Domain.objects.get(pk=pk)
        except (AssertionError, Domain.DoesNotExist):
            return HttpResponseNotFound('error')

        if user == request.user and name not in ('is_staff',):  # allowed change
            return JsonResponse({}, status=200)

        if name == 'is_active':
            user.is_active = reverse_value(user.is_active)
        if name == 'is_staff':
            user.is_staff = reverse_value(user.is_staff)
        if name == 'is_superuser':
            user.is_superuser = reverse_value(user.is_superuser)
        user.save()
        return JsonResponse({}, status=200)
    return JsonResponse({}, status=404)


@login_required
@user_passes_test(check_staff_or_admin)
def domain_delete(request, pk):
    if request.is_ajax():
        try:
            Domain.objects.get(pk=pk).delete()
            ActionLog.objects.create(
                action=ActionLog.DELETE_DOMAIN,
                user=request.user,
            )
        except Domain.DoesNotExist:
            return HttpResponseNotFound('error')
        return JsonResponse({}, status=200)
    return JsonResponse({}, status=404)


@login_required
def search_domain_name(request):
    if request.is_ajax():
        query = request.GET.get('term', '').strip()
        data = list()
        if len(query) >= 3:
            queryset = Domain.objects.filter(
                name__icontains=query
            )
            for domain in queryset[:10]:
                data.append({
                    'id': domain.pk,
                    'name': domain.name,
                })
        return JsonResponse(data=data, safe=False)

    raise Http404


@login_required
def search_company_name(request):
    if request.is_ajax():
        query = request.GET.get('term', '').strip()
        data = list()
        if len(query) >= 3:
            queryset = Domain.objects.filter(
                company_name__icontains=query
            )
            for domain in queryset[:10]:
                data.append({
                    'id': domain.pk,
                    'name': domain.company_name,
                })
        return JsonResponse(data=data, safe=False)

    raise Http404


@login_required
def search_telephone(request):
    if request.is_ajax():
        query = request.GET.get('term', '').strip()
        data = list()
        if len(query) >= 3:
            queryset = Domain.objects.filter(
                Q(telephone__icontains=query) |
                Q(telephone2__icontains=query) |
                Q(telephone3__icontains=query)
            )
            for domain in queryset[:10]:
                telephone = domain.telephone
                if query in domain.telephone2:
                    telephone = domain.telephone2
                if query in domain.telephone3:
                    telephone = domain.telephone3

                data.append({
                    'id': domain.pk,
                    'name': telephone,
                })
        return JsonResponse(data=data, safe=False)

    raise Http404


@login_required
def reminders_proxy(request):
    if request.user.is_superuser:
        return redirect('reminders-admin')
    if request.user.is_staff:
        return redirect('reminders-staff')


@login_required
@user_passes_test(check_staff_or_admin)
def import_domains(request):
    if request.method == 'POST':
        form = DomainImportForm(request.POST, request.FILES)
        if form.is_valid():
            for row in request.FILES['import_file'].chunks():
                data = "".join(chr(x) for x in row)
                data_list = data.split(';\n')
                for domain_name in data_list:
                    if len(domain_name) < 254:
                        Domain.objects.get_or_create(
                            name=domain_name
                        )
            return redirect('domain-list')
    else:
        form = DomainImportForm()
    return render(request, 'domains/domain_import.html', {
        'form': form,
        'current_page': 'import_domains'
    })


@login_required
@user_passes_test(check_staff_or_admin)
def export_domains(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="domain_list.csv"'

    writer = csv.writer(response)

    for domain in Domain.objects.all():
        row = [
            domain.name, domain.manager, domain.company_name,
            domain.telephone, domain.date_register, domain.date_expire,
            domain.admin, domain.pci_scan,
        ]
        writer.writerow(row)

    return response


@login_required
@user_passes_test(check_staff_or_admin)
def reminders_staff(request):
    qs = ActionLog.objects.filter(
        domain__manager=request.user,
    )
    read = request.GET.get('read')
    if read:
        if read == 'all':
            qs.filter(is_read=False).update(is_read=True)
        else:
            try:
                read = int(read)
                action = qs.get(pk=read)
                action.is_read = True
                action.save()
            except (ValueError, ActionLog.DoesNotExist):
                pass

    return render(request, 'domains/domain_log_list.html', {
        'actions': qs,
    })


@login_required
def get_whois(request):
    if request.is_ajax():
        domain_name = request.GET.get('domain_name')
        try:
            assert domain_name
        except AssertionError:
            return JsonResponse({}, status=404)

        data = dict()
        try:
            w = whois.whois(domain_name)
        except Exception as e:
            return JsonResponse({'error': e}, status=500)

        def get_datetime(extract_key):
            try:
                extract_date = w.get(extract_key)
                assert extract_date

                return datetime.datetime.strftime(
                    extract_date, '%Y-%m-%d')
            except (AssertionError, TypeError):
                return None

        for key in ('creation_date', 'expiration_date'):
            data[key] = get_datetime(key)
        return JsonResponse(data, safe=False)
    raise Http404


@login_required
def notifications(request):
    if not request.is_ajax():
        raise Http404

    notification = get_notifications(request.user)

    return JsonResponse({"count": notification.count()}, safe=False)


@login_required
@user_passes_test(check_staff_or_admin)
def domain_exists(request):
    if not request.is_ajax():
        raise Http404

    exists = False
    domain_name = request.GET.get('domain_name')
    if domain_name:
        exists = Domain.objects.filter(name=domain_name).exists()

    return JsonResponse({"exists": exists}, safe=False)
