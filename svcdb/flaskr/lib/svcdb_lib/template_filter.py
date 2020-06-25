import datetime

from flaskr.lib.conf.config import Config
from flask import Markup


def date_format(date: datetime.date, fmt=None):
    if date is None:
        return ""
    return date.strftime(fmt or Config.PY_DATE_FORMAT)


def date_time_format(date: datetime.datetime, fmt=None):
    if date is None:
        return ""
    return date.strftime(fmt or Config.PY_DATE_TIME_FORMAT)


def string_tooltip(mystr: str, length: int = 20):
    if mystr is None:
        return ""
    if len(mystr) > length:
        sub = mystr[:length] + "..."
        return Markup(f'''
        <span data-toggle="tooltip" title="{mystr}">
            {sub}
        </span> ''')
    return mystr
