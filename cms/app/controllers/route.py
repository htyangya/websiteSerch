# Flaskとrender_template（HTMLを表示させるための関数）をインポート
import json

from flask import render_template, current_app, Response, url_for, \
    request
from flask_login import logout_user
from werkzeug.utils import redirect

from app.forms.login_form import LoginForm
from app.lib.cms_lib.session import get_db_id
from app.lib.cms_lib.str_util import StrUtil
from app.lib.cms_lib.user_auth import UserAuth
from app.services.cms_admin import file_service
from app.services.cms import main_service, property_service
from app.services.login_service import doLogin


# 利用者メイン画面表示
@UserAuth.login_required
def index():
    return main_service.main_init(get_db_id(), request)


def swh_edit_mode():
    return main_service.swhEditMode()


@UserAuth.login_required
def folder():
    return main_service.getFolderList(get_db_id(), request)


@UserAuth.login_required
def get_file_list():
    if request.method == 'POST':
        view_type = request.form.get("view_type")
        sort_type = request.form.get("sort_type")
        sort_column = request.form.get("sort_column")
        id = request.form.get("id")
    else:
        view_type = request.args.get("view_type")
        sort_type = request.args.get("sort_type")
        sort_column = request.args.get("sort_column")
        sort_column_type = request.args.get("sort_column_type")
        id = request.args.get("id")

    return main_service.get_file_list_json(get_db_id(), view_type, id, sort_type, sort_column, sort_column_type)


# 検索画面を起動する
@UserAuth.login_required
def search_jqmodal():
    return main_service.open_search_jqmodal(request)


# 検索画面を起動する
@UserAuth.login_required
def search():
    return main_service.do_search(request)


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
        StrUtil.print_debug("file_path:{}".format(pdf_file_path))
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
        StrUtil.print_debug("file_path:{}".format(pdf_file_path))
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


@UserAuth.login_required
def keyword():
    return main_service.getKeywordList(get_db_id(), request)


@UserAuth.login_required
def ctx_search():
    return main_service.showCtxSearchList(get_db_id(), request)


@UserAuth.login_required
def property():
    if request.method == 'POST':
        func = request.form["func"]
    else:
        func = request.args.get("func")
    return property_service.property(func, request)


@UserAuth.login_required
def save_property():
    func = request.form["func"]
    return property_service.property_save(get_db_id(), func, request)


@UserAuth.login_required
def delete_property():
    return property_service.property_delete(request)


@UserAuth.login_required
def prop_upload_files():
    param = {}
    param["func"] = request.form.get("func")
    param["db_id"] = request.form.get('db_id')
    param["file_edit_id"] = request.form.get('fileEditId')
    param["object_id"] = request.form.get('objectId')
    param["file_type_id"] = request.form.get('file_type_id')
    param["file_names"] = request.form.getlist('file_name[]')
    param["file_paths"] = request.files.getlist('file_path[]')
    return property_service.file_upload(param)


@UserAuth.login_required
def prop_delete_file():
    return property_service.prop_delete_file(request)


# ファイルアップロード編集画面起動する
@UserAuth.login_required
def get_files():
    res, editFileList, msg = {}, [], "OK"
    file_type_id = request.form.get('file_type_id')
    editFileList = property_service.get_files(request.form.get('file_edit_id'),
                                              request.form.get('object_id'),
                                              request.form.get('file_type_id'))

    if file_type_id != None:
        res = {**res, **{"fileTypeId": file_type_id}}

    res = {**res, **{"dataList": editFileList}}
    res = {**res, **{"msg": msg}}
    return Response(json.dumps(res))


# 検索画面を起動する
@UserAuth.login_required
def folder_tree_jqmodal():
    return property_service.open_folder_tree(request)


# ログイン
def login():
    #    if current_user.is_authenticated:
    #        return redirect(url_for('index'))
    form = LoginForm()
    return doLogin(get_db_id(), form)


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
