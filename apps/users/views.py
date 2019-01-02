# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.http import HttpResponseNotFound
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from users.forms import UserChangeForm


def reverse_value(x):
    return False if x else True


def check_staff_or_admin(u):
    if any([u.is_staff, u.is_superuser]):
        return True
    raise Http404


@method_decorator(permission_required('is_superuser'), name='dispatch')
class UserListView(ListView):
    template_name = 'users/user_list.html'
    context_object_name = 'user_list'
    model = User
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = 'user_list'
        return context


@permission_required('is_superuser')
def change_user_status(request):
    if request.is_ajax():
        pk = request.GET.get('id')
        name = request.GET.get('name')
        try:
            assert pk
            hasattr(User, name)
            user = User.objects.get(pk=pk)
        except (AssertionError, User.DoesNotExist):
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
    raise Http404


@permission_required('is_superuser')
def user_add_edit(request, pk=None):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        user = None

    data = request.POST.copy()
    if request.user == user:
        data = None

    form = UserChangeForm(
        data=data or None,
        instance=user
    )
    if form.is_valid():
        if form.has_changed():
            form.save()
        return redirect('user-list')
    return render(request, 'users/user_add_edit.html', {
        'form': form
    })


@permission_required('is_superuser')
def user_delete(request, pk):
    if request.is_ajax():
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return HttpResponseNotFound('error')
        if request.user != user:
            user.delete()
        return JsonResponse({}, status=200)
    raise Http404


@login_required
def user_info(request):
    return render(request, 'users/user_info.html', {
        'user': request.user
    })
