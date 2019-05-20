from django.db import models
from jsonfield import JSONField

from users.models import User


class Domain(models.Model):
    ACTIVE = 'ACTIVE'
    REQUIRES_ACTIVE = 'REQUIRES_ACTIVE'
    TEMPORARY_CLOSED = 'TEMPORARY_CLOSED'
    REQUIRES_TEMPORARY_CLOSED = 'REQUIRES_TEMPORARY_CLOSED'
    REQUIRES_CLOSED = 'REQUIRES_CLOSED'
    CLOSED = 'CLOSED'

    CHOICE_STATUS = (
        (ACTIVE, ACTIVE),
        (REQUIRES_TEMPORARY_CLOSED, REQUIRES_TEMPORARY_CLOSED),
        (TEMPORARY_CLOSED, TEMPORARY_CLOSED),
        (REQUIRES_CLOSED, REQUIRES_CLOSED),
        (CLOSED, CLOSED),
        (REQUIRES_ACTIVE, REQUIRES_ACTIVE),
    )
    ALEXA_OFF = 'OFF'
    ALEXA_REQUIRES_ON = 'REQUIRES_ON'
    ALEXA_ON = 'ON'
    ALEXA_REQUIRES_OFF = 'ALEXA_REQUIRES_OFF'

    ALEXA_STATUSES = (
        (ALEXA_OFF, ALEXA_OFF),
        (ALEXA_REQUIRES_ON, ALEXA_REQUIRES_ON),
        (ALEXA_ON, 'ON'),
        (ALEXA_REQUIRES_OFF, ALEXA_REQUIRES_OFF),
    )

    name = models.CharField(max_length=255, unique=True)
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='manager'
    )
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_address = models.CharField(max_length=500, blank=True, null=True)
    telephone = models.CharField(max_length=255, blank=True, null=True)
    telephone2 = models.CharField(max_length=255, blank=True, null=True)
    telephone3 = models.CharField(max_length=255, blank=True, null=True)
    alexa = models.CharField(
        max_length=255, choices=ALEXA_STATUSES, default=ALEXA_OFF
    )
    alexa_comment = models.CharField(max_length=300, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, default='')
    email2 = models.EmailField(blank=True, null=True, default='')
    email3 = models.EmailField(blank=True, null=True, default='')
    redirect = models.CharField(max_length=255, blank=True, null=True)
    redirect_phone = models.CharField(max_length=255, blank=True, null=True)

    date_register = models.DateField(blank=True, null=True)
    date_expire = models.DateField(blank=True, null=True)
    date_last_scan = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='admin'
    )
    # Not use. Use date_last_scan instead
    pci_scan = models.BooleanField(default=False)
    pci_scan_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=255, choices=CHOICE_STATUS, default=ACTIVE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


class ActionLog(models.Model):
    ADD_DOMAIN = 'ADD_DOMAIN'
    EDIT_DOMAIN = 'EDIT_DOMAIN'
    DELETE_DOMAIN = 'DELETE_DOMAIN'
    LOGIN = 'LOGIN'
    ALEXA = 'ALEXA'

    ACTIONS = (
        (ADD_DOMAIN, 'ADD DOMAIN'),
        (EDIT_DOMAIN, 'EDIT DOMAIN'),
        (DELETE_DOMAIN, 'DELETE DOMAIN'),
        (LOGIN, 'LOGIN'),
        (ALEXA, 'ALEXA')
    )
    action = models.CharField(max_length=255, choices=ACTIONS)
    domain = models.ForeignKey(
        Domain, on_delete=models.SET_NULL, blank=True, null=True
    )
    data = JSONField(blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']


class AlexaTraffic(models.Model):
    domain = models.ForeignKey(
        Domain, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='alexa_traffic'
    )
    initiator = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='initiator'
    )
    executor = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='executor'
    )

    class Meta:
        ordering = ['-id']


class DomainConfirmUpdate(models.Model):
    domain = models.ForeignKey(
        Domain, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='confirm_up_set'
    )
    user_changed = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='user_changed'
    )
    responsible_admin = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='responsible_admin'
    )
    old_data = JSONField(blank=True, null=True)
    new_data = JSONField(blank=True, null=True)
    done = models.BooleanField(default=False)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']
