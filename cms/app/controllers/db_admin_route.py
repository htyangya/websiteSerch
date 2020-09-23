# Flaskとrender_template（HTMLを表示させるための関数）をインポート
from flask import url_for, request
from flask_login import logout_user
from werkzeug.utils import redirect

from app.forms.login_form import LoginForm
from app.lib.cms_lib.session import get_db_id
from app.lib.cms_lib.user_auth import UserAuth
from app.services.cms_db_admin import db_admin_main_service as adm_service
from app.services.login_service import doDbAdminLogin, redirectDbAdmin


@UserAuth.db_adm_login_required
def index():
    return adm_service.admin_main_init(get_db_id(), request)


@UserAuth.db_adm_login_required
def daily_log():
    return adm_service.daily_log_init(get_db_id())


@UserAuth.db_adm_login_required
def daily_log_search():
    return adm_service.daily_log_list(request.form)


@UserAuth.db_adm_login_required
def daily_log_dl():
    return adm_service.daily_log_download(request.form)


@UserAuth.db_adm_login_required
def privs_user():
    return adm_service.privs_user_list(get_db_id())


def privs_user_jqmodal():
    return adm_service.privs_user_jqmodal(get_db_id(), request)


def privs_user_search():
    return adm_service.get_privs_user_info(request)


@UserAuth.db_adm_login_required
def privs_user_save():
    if request.method == 'POST':
        func = request.form["func"]
    else:
        func = request.args.get("func")
    return adm_service.save_privs_user(func, request)


@UserAuth.db_adm_login_required
def privs_dept():
    return adm_service.privs_dept_list(get_db_id())


def privs_dept_jqmodal():
    return adm_service.privs_dept_jqmodal(get_db_id(), request)


def privs_corp_select():
    return adm_service.privs_corp_select(get_db_id(), request)


@UserAuth.db_adm_login_required
def privs_dept_save():
    if request.method == 'POST':
        func = request.form["func"]
    else:
        func = request.args.get("func")
    return adm_service.save_privs_dept(func, request)


@UserAuth.db_adm_login_required
def privs_dept_detail():
    return adm_service.privs_dept_detail(get_db_id(), request)


@UserAuth.db_adm_login_required
def check_object_batch_upload():
    return adm_service.check_batch_upload_post(get_db_id(), request)


@UserAuth.db_adm_login_required
def object_batch_upload():
    if request.method == 'POST':
        return adm_service.batch_upload_post(get_db_id(), request)
    else:
        return adm_service.batch_upload_get(get_db_id(), request)


@UserAuth.db_adm_login_required
def template_dl():
    return adm_service.template_download(request.form)


@UserAuth.db_adm_login_required
def upload_data():
    return adm_service.upload_data(get_db_id(), request)


# ログイン
def redirect_db_admin():
    return redirectDbAdmin(request.args.get('db_id', ''))


# ログイン
def login():
    form = LoginForm()
    return doDbAdminLogin(get_db_id(), form)


# ログアウト
def logout():
    logout_user()
    return redirect(url_for("db_adm_login"))
