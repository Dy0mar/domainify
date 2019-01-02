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
