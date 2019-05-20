# -*- coding: utf-8 -*-
import time
import datetime

from django.db.models import Q
from whois import whois
from celery import shared_task

from domains.models import Domain, ActionLog
from users.models import User


@shared_task
def auto_update_whois():
    now = datetime.datetime.now().date()
    expire_period = (
        now + datetime.timedelta(days=30)
    )

    qs = Domain.objects.filter(
        Q(date_register__isnull=True) |
        Q(date_expire__isnull=True) |
        Q(
            Q(date_expire__gte=now),
            Q(date_expire__lte=expire_period)
        )
    ).exclude(status=Domain.CLOSED)

    for domain in qs:
        try:
            w = whois(domain.name)
        except Exception:
            continue

        domain.date_register = w.creation_date.date()
        domain.date_expire = w.expiration_date.date()
        domain.save()
        time.sleep(2)


@shared_task
def auto_close_domain():
    qs = Domain.objects.filter(
        date_expire__lt=datetime.datetime.now(),
    ).exclude(status=Domain.CLOSED)

    for domain in qs:
        domain.status = Domain.CLOSED
        domain.save()
        user = User.objects.filter(username='superadmin').first()
        if user:
            ActionLog.objects.create(
                action='AUTO_CLOSE_DOMAIN',
                user=user,
                domain=domain
            )
        time.sleep(1)
