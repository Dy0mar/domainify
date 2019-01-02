from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField


class Domain(models.Model):
    ACTIVE = 'ACTIVE'
    TEMPORARY_CLOSED = 'TEMPORARY_CLOSED'
    CLOSED = 'CLOSED'
    CHOICE_STATUS = (
        (ACTIVE, 'ACTIVE'),
        (TEMPORARY_CLOSED, 'TEMPORARY CLOSED'),
        (CLOSED, 'CLOSED'),
    )

    name = models.CharField(max_length=255, unique=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL,
                                blank=True, null=True, related_name='manager')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_address = models.CharField(max_length=500, blank=True, null=True)
    telephone = models.CharField(max_length=255, blank=True, null=True)
    telephone2 = models.CharField(max_length=255, blank=True, null=True)
    telephone3 = models.CharField(max_length=255, blank=True, null=True)
    date_register = models.DateField(blank=True, null=True)
    date_expire = models.DateField(blank=True, null=True)
    date_last_scan = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL,
                              blank=True, null=True, related_name='admin')
    # Not use. Use date_last_scan instead
    pci_scan = models.BooleanField(default=False)
    pci_scan_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=255, choices=CHOICE_STATUS, default=ACTIVE)

    def __str__(self):
        return self.name


class ActionLog(models.Model):
    ADD_DOMAIN = 'ADD_DOMAIN'
    EDIT_DOMAIN = 'EDIT_DOMAIN'
    DELETE_DOMAIN = 'DELETE_DOMAIN'
    LOGIN = 'LOGIN'

    ACTIONS = (
        (ADD_DOMAIN, 'ADD DOMAIN'),
        (EDIT_DOMAIN, 'EDIT DOMAIN'),
        (DELETE_DOMAIN, 'DELETE DOMAIN'),
        (LOGIN, 'LOGIN')
    )
    action = models.CharField(max_length=255, choices=ACTIONS)
    domain = models.ForeignKey(Domain, on_delete=models.SET_NULL,
                               blank=True, null=True)
    data = JSONField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL,
                             blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
