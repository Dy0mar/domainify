# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.filter
def get_key(d, key):
    try:
        return d.get(key)
    except AttributeError:
        return None
