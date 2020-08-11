# Flaskとrender_template（HTMLを表示させるための関数）をインポート

from flask import render_template, current_app, request
from flask import url_for
from flask_login import current_user
from flask_login import logout_user
from werkzeug.utils import redirect

from flaskr.forms.login_form import LoginForm
from flaskr.lib.conf.const import Const
from flaskr.lib.svcdb_lib.session import get_db_id
from flaskr.lib.svcdb_lib.user_auth import UserAuth
from flaskr.services import main_service, file_service, schedule_service
from flaskr.services.login_service import doLogin
from flaskr.services.main_service import index_init


def index():
    return index_init(request)


@UserAuth.login_required
def get_file_list():
    if request.method == 'POST':
        view_type = request.form.get("view_type")
        id = request.form.get("id")
    else:
        view_type = request.args.get("view_type")
        id = request.args.get("id")
    return main_service.get_file_list_json(get_db_id(), view_type, id)


# ファイルアップロード編集画面起動する
@UserAuth.login_required
def files_jqmodal():
    return file_service.open_files_jqmodal(
        request.args.get('db_id'),
        request.args.get('object_id'),
        request.args.get('file_id'),
        request.args.get('file_type_id'))


# PDFファイルをpdfjsで開く
@UserAuth.login_required
def view_pdf(file_id):
    params = {}
    params['file_id'] = file_id
    params = file_service.decompress_file(params)
    if params['df'] != '':
        downloadDirPath = current_app.config['DOWNLOAD_DIR_PATH']
        pdf_file_path = params['df'].replace(downloadDirPath, '/view_pdf')
        print("###############file_path:" + pdf_file_path)
        return render_template('view_pdf.html', pdf_full_path=pdf_file_path)


# PDFファイルを開く
def file_pdf(file_id):
    params = {}
    params['file_id'] = file_id
    params['disp_mode'] = request.args.get('disp_mode')
    params = file_service.decompress_file(params)
    if params['df'] is not None and params['df'] != '':
        downloadDirPath = current_app.config['DOWNLOAD_DIR_PATH']
        pdf_file_path = params['df'].replace(downloadDirPath, '/file_pdf')
        print("###############file_path:" + pdf_file_path)
        return render_template('view_pdf.html', pdf_full_path=pdf_file_path)
    else:
        return render_template('error/fileNotFound.html')


# ファイルダウンロード
def download_file():
    return file_service.download_file(
        request.args.get('db_id'),
        request.args.get('file_id'),
        request.args.get('disp_mode'),
        request.args.get('file_edit_id'))


# ログイン
def login():
    #    if current_user.is_authenticated:
    #        return redirect(url_for('index'))
    form = LoginForm()
    return doLogin(form)


# ログアウト
def logout():
    logout_user()
    return redirect(url_for("login", db_id=get_db_id()))


def no_privs():
    errorMsg = request.args.get('msg')
    return render_template('error/noPrivs.html', errorMsg=errorMsg)


# page not exist
def page_not_found(e):
    return render_template('error/404.html'), 404


@UserAuth.login_required
def main_menu():
    return main_service.do_main(request)


@UserAuth.login_required
def outage_schedule():
    return main_service.main_init(Const.OUTAGE_SCHEDULE, request)


@UserAuth.login_required
def outage_schedule_jqmodal():
    return schedule_service.open_outage_schedule_jqmodal(request)


@UserAuth.login_required
def outage_schedule_detail():
    return schedule_service.open_outage_schedule_detail(request)


@UserAuth.login_required
def outage_schedule_edit():
    return schedule_service.open_outage_schedule_edit(request)


# get method args:
#   turbine_id,
#   data_type,
#   date_start,
#   date_end
@UserAuth.login_required
def outage_schedule_add():
    return schedule_service.open_outage_schedule_add(request)


# post method args:
# teiken_id int
@UserAuth.login_required
def outage_schedule_delete():
    return schedule_service.open_outage_schedule_delete(request)
