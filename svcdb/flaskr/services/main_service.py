from flask import render_template, url_for
from flask_login import current_user
from werkzeug.utils import redirect

from flaskr.lib.conf.const import Const
from flaskr.lib.svcdb_lib.session import get_session_id
from flaskr.services.schedule_service import show_schedule
from flaskr.lib.svcdb_lib.db_util import DbUtil


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


def do_main(request):
    return render_template(
        'svcdb_main.html',
        user_name=current_user.get_user_name(),
        turbine_list_url=list_url(),
        Const=Const,
    )


def list_url():
    session_id_in = get_session_id(Const.SESSION_COOKIE_NAME)
    return DbUtil.sqlExcuter(
        "SELECT PKG_TURBINE_DB_UTIL.GET_TURBINE_LIST_URL('{session_id_in}') FROM DUAL",
        session_id_in=session_id_in).first()[0] or ""
