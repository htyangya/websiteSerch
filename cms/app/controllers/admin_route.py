# Flaskとrender_template（HTMLを表示させるための関数）をインポート
from flask import url_for, request
from flask_login import logout_user
from werkzeug.utils import redirect

from app.forms.login_form import LoginForm
from app.lib.cms_lib.user_auth import UserAuth
from app.lib.conf.const import Const
from app.services.cms_admin import admin_main_service as adm_service
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


def delete_database_jqmodal():
    return adm_service.delete_database_jqmodal(request)


def keyword():
    if request.method == 'POST':
        func = request.form["func"]
    else:
        func = request.args.get("func")
    return adm_service.service_keyword(func, request)


@UserAuth.adm_login_required
def ip_addr_admin():
    return adm_service.ip_addr_master_list()


@UserAuth.adm_login_required
def ip_addr_list():
    ip_addr_list_id = request.args.get("ip_addr_list_id")
    return adm_service.ip_addr_list(ip_addr_list_id)


@UserAuth.adm_login_required
def ip_addr():
    if request.method == 'POST':
        func = request.form["func"]
        ip_addr_list_id = request.form["ip_addr_list_id"]
    else:
        func = request.args.get("func")
        ip_addr_list_id = request.args.get("ip_addr_list_id")
    return adm_service.service_ip_addr(func, ip_addr_list_id, request)


@UserAuth.adm_login_required
def keyword_list():
    return adm_service.keywordList(request)


@UserAuth.adm_login_required
def list_format_list():
    return adm_service.list_format_list(request)


@UserAuth.adm_login_required
def property_format_list():
    return adm_service.property_format_list(request)


@UserAuth.adm_login_required
def list_format_edit():
    if request.method == 'POST':
        func = request.form["func"]
        db_id = request.form["db_id"]
        object_type_id = request.form["object_type_id"]
        format_id = request.form["formatId"]
    else:
        func = request.args.get("func")
        db_id = request.args.get("db_id")
        object_type_id = request.args.get("object_type_id")
        format_id = request.args.get("format_id")
    return adm_service.format_edit(func, db_id, Const.LIST, object_type_id, format_id, request)


@UserAuth.adm_login_required
def property_format_edit():
    if request.method == 'POST':
        func = request.form["func"]
        db_id = request.form["db_id"]
        object_type_id = request.form["object_type_id"]
        format_id = request.form["formatId"]
    else:
        func = request.args.get("func")
        db_id = request.args.get("db_id")
        object_type_id = request.args.get("object_type_id")
        format_id = request.args.get("format_id")
    return adm_service.format_edit(func, db_id, Const.PROPERTY, object_type_id, format_id, request)


@UserAuth.adm_login_required
def list_format_delete():
    if request.method == 'POST':
        func = request.form["func"]
        db_id = request.form["db_id"]
        format_id = request.form["format_id"]
    else:
        func = request.args.get("func")
        db_id = request.args.get("db_id")
        format_id = request.args.get("format_id")
    return adm_service.format_delete(func, db_id, Const.LIST, format_id)


@UserAuth.adm_login_required
def property_format_delete():
    if request.method == 'POST':
        func = request.form["func"]
        db_id = request.form["db_id"]
        format_id = request.form["format_id"]
    else:
        func = request.args.get("func")
        db_id = request.args.get("db_id")
        format_id = request.args.get("format_id")
    return adm_service.format_delete(func, db_id, Const.PROPERTY, format_id)


def format_jqmodal():
    return adm_service.format_jqmodal(request)


@UserAuth.adm_login_required
def style_setting_list():
    return adm_service.style_setting_list(request)


@UserAuth.adm_login_required
def style_setting_edit():
    if request.method == 'POST':
        func = request.form["func"]
    else:
        func = request.args.get("func")
    return adm_service.style_setting_edit(func, request)


# ログイン
def login():
    form = LoginForm()
    return doAdminLogin(form)


# ログアウト
def logout():
    logout_user()
    return redirect(url_for("adm_login"))


@UserAuth.adm_login_required
def selection_mng():
    return adm_service.selection_mng()


@UserAuth.adm_login_required
def selection_mst_persistent():
    return adm_service.selection_mst_persistent()


@UserAuth.adm_login_required
def selection_mst_detail():
    return adm_service.selection_mst_detail()


@UserAuth.adm_login_required
def selection_list_persistent():
    return adm_service.selection_list_persistent()


@UserAuth.adm_login_required
def selection_delete():
    return adm_service.selection_delete()
