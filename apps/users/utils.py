# -*- coding: utf-8 -*-


def reverse_value(x):
    return False if x else True


def get_notification_list(nl):
    return [int(pk) for pk in nl.split(',') if pk]

