from flask import render_template, url_for
from flask_login import current_user
from werkzeug.utils import redirect

from flaskr.lib.conf.const import Const
from flaskr.services.schedule_service import show_schedule


def main_init(sub_menu, request):
    if len(sub_menu) == 0:
        return render_template('error/404.html')

    # Outage Schedule
    if Const.OUTAGE_SCHEDULE == sub_menu:
        return show_schedule(request)

    # その他のメニュー予定
    else:
        return redirect(url_for('main'))


def index_init(request):
    if current_user.is_active:
        return redirect(url_for('main'))
    return redirect(url_for('login'))
