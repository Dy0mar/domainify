# -*- coding: utf-8 -*-
import datetime


def to_date(raw_date):
    try:
        assert raw_date
        return datetime.datetime.strptime(raw_date, '%d.%m.%Y').date()
    except (AssertionError, ValueError):
        return None


def validate_small_date(date_from, date_till):
    try:
        assert (date_from is not None or date_till is not None)
        try:
            assert date_from
            return True
        except (AssertionError, TypeError):
            pass
    except AssertionError:
        pass
    return False


def validate_big_date(date_from, date_till):
    try:
        assert (date_from is not None or date_till is not None)
        try:
            assert date_from <= date_till
            return True
        except (AssertionError, TypeError):
            pass
    except AssertionError:
        pass
    return False


def formation_data(initial_data, cleaned_data, notify_msg):
    fields = (
        'company_name', 'telephone', 'telephone2', 'telephone3',
        'email', 'email2', 'email3', 'company_address'
    )

    old_data = {}
    new_data = {}

    for field in fields:
        old_value = str(initial_data.get(field, '') or '')
        new_value = str(cleaned_data.get(field, '') or '')

        # Отправлять полную инфу
        if new_value:
            notify_msg += '\n{} - {}'.format(field, new_value)

        if old_value != new_value:
            old_data[field] = old_value
            new_data[field] = new_value

    return old_data, new_data, notify_msg
