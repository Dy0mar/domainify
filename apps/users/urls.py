# -*- coding: utf-8 -*-
from django.urls import path
from django.urls import re_path

from users import views

urlpatterns = [
    path('list/', views.UserListView.as_view(), name='user-list'),
    path('user-add/', views.user_add, name='user-add'),
    path('notify/', views.notify, name='notify'),
    path('change-user-status/',
         views.change_user_status,
         name='change-user-status'
         ),
    path(
        'change-notification-list/', views.change_notification_list,
        name='change-notification-list'
    ),
    path(
        'change-notification-method/',
        views.change_notification_method,
        name='change-notification-method'
    ),
    path(
        'check-notification-method/',
        views.check_notification_method,
        name='check-notification-method'
    ),
    re_path(
        r'^user-edit/(?P<pk>\d+)/$',
        views.user_edit,
        name='user-edit'
    ),
    re_path(
        r'^user-delete/(?P<pk>\d+)/$',
        views.user_delete,
        name='user-delete'
    ),
    re_path(
        r'^confirm-up/done/$',
        views.confirm_up_done,
        name='confirm-up-done'
    ),
    path('profile/', views.user_info, name='user-profile'),
]
