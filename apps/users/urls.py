# -*- coding: utf-8 -*-
from django.urls import path
from django.urls import re_path

from users import views

urlpatterns = [
    path('list/', views.UserListView.as_view(), name='user-list'),
    path('user-add/', views.user_add_edit, name='user-add'),
    path('change-user-status/',
         views.change_user_status,
         name='change-user-status'),
    re_path(
        r'^user-edit/(?P<pk>\d+)/$',
        views.user_add_edit,
        name='user-edit'
    ),
    re_path(
        r'^user-delete/(?P<pk>\d+)/$',
        views.user_delete,
        name='user-delete'
    ),
    path('', views.user_info, name='user-info'),
]
