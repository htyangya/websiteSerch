# Flaskとrender_template（HTMLを表示させるための関数）をインポート
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from app.lib.conf import key
from app.lib.conf.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
# login_viewのrouteを設定
login_manager.login_view = 'login'

from app.controllers import route
from app.controllers import admin_route
from app.controllers import db_admin_route


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    app.secret_key = key.SECRET_KEY
    app.add_url_rule('/login', 'login', route.login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', 'logout', route.logout)
    app.add_url_rule('/index', 'index', methods=['GET', 'POST'])
    app.add_url_rule('/', 'index', route.index, methods=['GET', 'POST'])
    app.add_url_rule('/swh_edit_mode', 'swh_edit_mode', route.swh_edit_mode, methods=['GET'])
    app.add_url_rule('/view_pdf/<file_id>', 'view_pdf', route.view_pdf)
    app.add_url_rule('/folder', 'folder', route.folder, methods=['POST'])
    app.add_url_rule('/get_file_list', 'get_file_list', route.get_file_list, methods=['GET', 'POST'])
    app.add_url_rule('/files_jqmodal', 'files_jqmodal', route.files_jqmodal, methods=['GET'])
    app.add_url_rule('/file_pdf/<file_id>', 'file_pdf', route.file_pdf)
    app.add_url_rule('/download_file', 'download_file', route.download_file, methods=['GET'])
    app.add_url_rule('/keyword', 'keyword', route.keyword, methods=['POST'])
    app.add_url_rule('/ctx_search', 'ctx_search', route.ctx_search, methods=['GET', 'POST'])
    app.add_url_rule('/search_jqmodal', 'search_jqmodal', route.search_jqmodal, methods=['GET'])
    app.add_url_rule('/search', 'search', route.search, methods=['GET'])

    # 編集モードの場合
    app.add_url_rule('/property', 'property', route.property, methods=['GET'])
    app.add_url_rule('/save_property', 'save_property', route.save_property, methods=['POST'])
    app.add_url_rule('/delete_property', 'delete_property', route.delete_property, methods=['POST'])
    app.add_url_rule('/property/upload_files', 'prop_upload_files', route.prop_upload_files, methods=['POST'])
    app.add_url_rule('/property/delete_file', 'prop_delete_file', route.prop_delete_file, methods=['POST'])
    app.add_url_rule('/property/folder_tree_jqmodal', 'folder_tree_jqmodal', route.folder_tree_jqmodal, methods=['GET'])
    app.add_url_rule('/get_files', 'get_files', route.get_files, methods=['POST'])

    # DB別システム管理機能
    app.add_url_rule('/cmsdbadmin/index', 'db_adm_index', methods=['GET', 'POST'])
    app.add_url_rule('/cmsdbadmin/', 'db_adm_index', db_admin_route.index, methods=['GET', 'POST'])
    app.add_url_rule('/cmsdbadmin/redirect_db_admin', 'redirect_db_admin', db_admin_route.redirect_db_admin,
                     methods=['GET'])
    app.add_url_rule('/cmsdbadmin/login', 'db_adm_login', db_admin_route.login, methods=['GET', 'POST'])
    app.add_url_rule('/cmsdbadmin/daily_log', 'daily_log', db_admin_route.daily_log, methods=['GET'])
    app.add_url_rule('/cmsdbadmin/daily_log_search', 'daily_log_search', db_admin_route.daily_log_search,
                     methods=['POST'])
    app.add_url_rule('/cmsdbadmin/daily_log_dl', 'daily_log_dl', db_admin_route.daily_log_dl, methods=['POST'])
    app.add_url_rule('/cmsdbadmin/privs_user', 'privs_user', db_admin_route.privs_user, methods=['GET'])
    app.add_url_rule('/cmsdbadmin/privs_user_jqmodal', 'privs_user_jqmodal', db_admin_route.privs_user_jqmodal,
                     methods=['GET', 'POST'])
    app.add_url_rule('/cmsdbadmin/privs_user_search', 'privs_user_search', db_admin_route.privs_user_search,
                     methods=['GET', 'POST'])
    app.add_url_rule('/cmsdbadmin/privs_user_save', 'privs_user_save', db_admin_route.privs_user_save,
                     methods=['GET', 'POST'])
    app.add_url_rule('/cmsdbadmin/privs_dept', 'privs_dept', db_admin_route.privs_dept, methods=['GET'])
    app.add_url_rule('/cmsdbadmin/privs_dept_jqmodal', 'privs_dept_jqmodal', db_admin_route.privs_dept_jqmodal,
                     methods=['GET', 'POST'])
    app.add_url_rule('/cmsdbadmin/privs_corp_select', 'privs_corp_select', db_admin_route.privs_corp_select,
                     methods=['GET', 'POST'])
    app.add_url_rule('/cmsdbadmin/privs_dept_save', 'privs_dept_save', db_admin_route.privs_dept_save,
                     methods=['GET', 'POST'])
    app.add_url_rule('/cmsdbadmin/privs_dept_detail', 'privs_dept_detail', db_admin_route.privs_dept_detail,
                     methods=['GET'])
    app.add_url_rule('/cmsdbadmin/template_dl', 'template_dl', db_admin_route.template_dl, methods=['POST'])
    app.add_url_rule('/cmsdbadmin/object_batch_upload', 'object_batch_upload', db_admin_route.object_batch_upload,
                     methods=['GET', 'POST'])
    app.add_url_rule('/cmsdbadmin/upload_data', 'upload_data', db_admin_route.upload_data, methods=['POST'])

    # システム管理機能
    app.add_url_rule('/cmsadmin/index', 'adm_index', methods=['GET', 'POST'])
    app.add_url_rule('/cmsadmin/', 'adm_index', admin_route.index, methods=['GET', 'POST'])
    app.add_url_rule('/cmsadmin/login', 'adm_login', admin_route.login, methods=['GET', 'POST'])
    # DB管理
    app.add_url_rule('/cmsadmin/database_admin', 'database_admin', admin_route.database_admin, methods=['GET'])
    app.add_url_rule('/cmsadmin/database', 'database', admin_route.database, methods=['GET', 'POST'])
    app.add_url_rule('/cmsadmin/keyword', 'adm_keyword', admin_route.keyword, methods=['GET', 'POST'])
    # IPアドレス管理
    app.add_url_rule('/cmsadmin/ip_addr_admin', 'ip_addr_admin', admin_route.ip_addr_admin, methods=['GET'])
    app.add_url_rule('/cmsadmin/ip_addr_list', 'ip_addr_list', admin_route.ip_addr_list, methods=['GET'])
    app.add_url_rule('/cmsadmin/ip_addr', 'ip_addr', admin_route.ip_addr, methods=['GET', 'POST'])

    app.add_url_rule('/no_privs', 'no_privs', route.no_privs, methods=['GET'])
    app.register_error_handler(404, route.page_not_found)
    return app
