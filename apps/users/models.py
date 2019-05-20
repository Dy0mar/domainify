# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, Permission

from users.tasks import send_xmppp_message, send_mail_to_user


class User(AbstractUser):
    pidgin = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.username

    class Meta(object):
        ordering = ('id',)

        permissions = (
            ('supermanagers', 'Can get access to advanced functional'),
            ('can_manage_alexa_traffic', 'Can manage Alexa traffic'),
            ('can_manage_domain_registrar', 'Can manage Domain Name Registrar'),
            ('can_edit_site', 'Can edit site'),
        )

    @property
    def is_staff_or_admin(self):
        return any([self.is_staff, self.is_superuser])

    def has_group_perm(self, perm):
        return self.groups.filter(permissions__codename=perm).exists()

    def send_notification(self, message):
        s = self.user_settings.first()

        error = False
        msg = ''
        # не включал уведомления
        if not s:
            error = True
            msg = '{} не включал уведомления. Пусть убедиться в том, ' \
                  'что у него в профайле введена почта и/или pidgin и ' \
                  'включены уведомления'.format(self.username)
            return {'error': error, 'msg': msg}

        # отключил уведомления
        if not any([s.pidgin, s.email]):
            error = True
            msg = '{} не включал уведомления. Пусть убедиться в том, ' \
                  'что у него в профайле введена почта и/или pidgin и ' \
                  'включены уведомления'.format(self.username)
            return {'error': error, 'msg': msg}

        if s.pidgin:
            send_xmppp_message.apply_async((self.pidgin, message))

        if s.email:
            subject = 'Work Bot'
            from_email = settings.EMAIL_HOST_USER
            send_mail_to_user.apply_async(
                (subject, message, from_email, [self.email])
            )

        return {'error': error, 'msg': msg}


class Settings(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        blank=True, null=True, related_name='user_settings'
    )
    # Список юзеров
    user_notification_list = models.CharField(max_length=255)
    pidgin = models.BooleanField(default=False)
    email = models.BooleanField(default=False)

    def __str__(self):
        return self.user
