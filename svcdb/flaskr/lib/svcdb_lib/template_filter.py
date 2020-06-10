import datetime

from flaskr.lib.conf.config import Config


def date_format(date: datetime.date, fmt=None):
    if date is None:
        return ""
    return date.strftime(fmt or Config.PY_DATE_FORMAT)


def date_time_format(date: datetime.datetime, fmt=None):
    if date is None:
        return ""
    return date.strftime(fmt or Config.PY_DATE_TIME_FORMAT)
