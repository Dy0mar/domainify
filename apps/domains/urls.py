# -*- coding: utf-8 -*-
from django.urls import path
from django.urls import re_path

from domains import views

urlpatterns = [
    path('domain-add/', views.domain_add_edit, name='domain-add'),
    path('reminders/', views.reminders_proxy, name='reminders'),
    path('import-domains/', views.import_domains, name='import-domains'),
    path('export-domains/', views.export_domains, name='export-domains'),
    path('reminders/admin/', views.domain_list, {
        'reminders': 'admin'
    }, name='reminders-admin'),
    path('my-list/', views.domain_list, {
        'my_list': True
    }, name='my-domain-list'),
    path('reminders/staff/', views.reminders_staff, name='reminders-staff'),
    path('get-whois/', views.get_whois, name='get-whois'),
    re_path(
        r'^domain-detail/(?P<pk>\d+)/$',
        views.domain_detail,
        name='domain-detail'
    ),
    re_path(
        r'^domain-edit/(?P<pk>\d+)/$',
        views.domain_add_edit,
        name='domain-edit'
    ),
    re_path(
        r'^domain-delete/(?P<pk>\d+)/$',
        views.domain_delete,
        name='domain-delete'
    ),
    path(
        'search-domain-name/', views.search_domain_name,
        name='search-domain-name'
    ),
    path(
        'search-company-name/', views.search_company_name,
        name='search-company-name'
    ),
    path(
        'search-telephone/', views.search_telephone,
        name='search-telephone'
    ),
    path(
        'notifications/', views.notifications,
        name='notifications'
    ),
    path(
        'exists/', views.domain_exists,
        name='domain-exists'
    ),
    re_path(
        r'^domain-edit/(?P<pk>\d+)/logs/$',
        views.domain_logs,
        name='domain-logs'
    ),

    path('', views.domain_list, name='domain-list'),
]
