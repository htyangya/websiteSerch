# Flaskとrender_template（HTMLを表示させるための関数）をインポート
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from flaskr.lib.conf import key
from flaskr.lib.conf.config import Config
from flaskr.lib.svcdb_lib.template_filter import date_format, date_time_format

db = SQLAlchemy()
login_manager = LoginManager()
# login_viewのrouteを設定
login_manager.login_view = 'login'

from flaskr.controllers import route


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # templates and jinja2 hot reload
    app.config['TEMPLATES_AUTO_RELOAD'] = Config.DEBUG
    app.jinja_env.auto_reload = Config.DEBUG
    db.init_app(app)
    login_manager.init_app(app)
    app.secret_key = key.SECRET_KEY
    app.add_template_filter(date_format, "sys_dfmt")
    app.add_template_filter(date_time_format, "sys_dtfmt")
    app.add_url_rule('/login', 'login', route.login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', 'logout', route.logout)
    app.add_url_rule('/index', 'index', methods=['GET', 'POST'])
    app.add_url_rule('/', 'index', route.index, methods=['GET', 'POST'])
    app.add_url_rule('/view_pdf/<file_id>', 'view_pdf', route.view_pdf)
    app.add_url_rule('/get_file_list', 'get_file_list', route.get_file_list, methods=['GET', 'POST'])
    app.add_url_rule('/files_jqmodal', 'files_jqmodal', route.files_jqmodal, methods=['GET'])
    app.add_url_rule('/file_pdf/<file_id>', 'file_pdf', route.file_pdf)
    app.add_url_rule('/download_file', 'download_file', route.download_file, methods=['GET'])
    app.add_url_rule('/main', 'main', route.main_menu, methods=['GET', 'POST'])
    app.add_url_rule('/outage_schedule', 'outage_schedule', route.outage_schedule, methods=['GET', 'POST'])
    app.add_url_rule('/outage_schedule_jqmodal', 'outage_schedule_jqmodal', route.outage_schedule_jqmodal,
                     methods=['GET', 'POST'])
    app.add_url_rule('/outage_schedule_detail', 'outage_schedule_detail', route.outage_schedule_detail,
                     methods=['GET', 'POST'])
    app.add_url_rule('/outage_schedule_edit', 'outage_schedule_edit', route.outage_schedule_edit,
                     methods=['GET', 'POST'])
    app.add_url_rule('/outage_schedule_add', 'outage_schedule_add', route.outage_schedule_add,
                     methods=['GET', 'POST'])
    app.add_url_rule('/outage_schedule_delete', 'outage_schedule_delete', route.outage_schedule_delete,
                     methods=['POST'])
    app.add_url_rule('/no_privs', 'no_privs', route.no_privs, methods=['GET'])
    app.register_error_handler(404, route.page_not_found)

    return app
