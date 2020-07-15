# Flaskとrender_template（HTMLを表示させるための関数）をインポート
from flask import url_for, request
from flask_login import logout_user
from werkzeug.utils import redirect

from app.forms.login_form import LoginForm
from app.lib.cms_lib.user_auth import UserAuth
from app.services import admin_ip_addr_service as ip_addr_service
from app.services import admin_main_service as adm_service
from app.services.login_service import doAdminLogin


@UserAuth.adm_login_required
def index():
    return adm_service.admin_main_init()


@UserAuth.adm_login_required
def database_admin():
    return adm_service.database_list()


@UserAuth.adm_login_required
def daily_log_dl():
    return adm_service.daily_log_download(request.form)


@UserAuth.adm_login_required
def database():
    if request.method == 'POST':
        func = request.form["func"]
    else:
        func = request.args.get("func")
    return adm_service.service_database(func, request)


def keyword():
    if request.method == 'POST':
        func = request.form["func"]
    else:
        func = request.args.get("func")
    return adm_service.service_keyword(func, request)


@UserAuth.adm_login_required
def ip_addr_admin():
    return ip_addr_service.ip_addr_master_list()


@UserAuth.adm_login_required
def ip_addr_list():
    ip_addr_list_id = request.args.get("ip_addr_list_id")
    return ip_addr_service.ip_addr_list(ip_addr_list_id)


@UserAuth.adm_login_required
def ip_addr():
    if request.method == 'POST':
        func = request.form["func"]
        ip_addr_list_id = request.form["ip_addr_list_id"]
    else:
        func = request.args.get("func")
        ip_addr_list_id = request.args.get("ip_addr_list_id")
    return ip_addr_service.service_ip_addr(func, ip_addr_list_id, request)


# ログイン
def login():
    form = LoginForm()
    return doAdminLogin(form)


# ログアウト
def logout():
    logout_user()
    return redirect(url_for("adm_login"))
