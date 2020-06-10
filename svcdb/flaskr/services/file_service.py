import os
import re
import sys

from flask import render_template, jsonify, current_app, make_response, send_file
from flask_login import current_user

from flaskr import db
from flaskr.controllers.package import PkgSvcdbLog
from flaskr.lib.conf.const import Const
from flaskr.lib.svcdb_lib.file_util import FileUtil
from flaskr.lib.svcdb_lib.str_util import StrUtil
from flaskr.models.svcdb_file import SvcdbFile
from flaskr.models.svcdb_file_type import SvcdbFileType
from flaskr.models.svcdb_file_wk import SvcdbFileWk


def open_files_jqmodal(db_id, object_id, file_id, file_type_id):
    if len(object_id) == 0:
        return render_template('error/404.html')

    svcdbFile = SvcdbFile()
    attacheFileList = svcdbFile.get_file_list(object_id, file_type_id)
    return render_template(
        'files_jqmodal.html',
        jqmTitle='添付ファイル画面',
        db_id=db_id,
        object_id=object_id,
        file_id=file_id,
        attacheFileList=attacheFileList)


def ctx_allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Const.CTX_FILE_ALLOWED_EXTENSIONS


def decompress_file(params):
    params['df'] = None
    if params['disp_mode'] == 'edit':
        print(params['disp_mode'])
        svcdbFileWkE = SvcdbFileWk()
        attacheFile = svcdbFileWkE.getFile(params['edit_id'], params['file_id'])
    else:
        svcdbFileE = SvcdbFile()
        attacheFile = svcdbFileE.getFile(params['file_id'])
    if attacheFile is not None:
        try:
            file_path = os.path.join(attacheFile.dir_name, attacheFile.c_file_name)
            unzip_dir_path = str(StrUtil.get_safe_config(current_app, 'DOWNLOAD_DIR_PATH'))
            unzip_file_path = FileUtil.unzip_file(file_path, unzip_dir_path, attacheFile.file_id)

            params['attacheFile'] = attacheFile
            params['df'] = unzip_file_path
        except FileNotFoundError:
            print("FileNotFoundError")

    return params


def download_file(db_id, file_id, disp_mode, file_edit_id):
    params = {}
    params['file_id'] = file_id
    params['disp_mode'] = disp_mode
    params['edit_id'] = file_edit_id
    decompress_file(params)
    if params['df'] is None or params['attacheFile'].file_name == '':
        return make_response(jsonify(message='File Not Found!'))

    try:
        svcdbFileType = SvcdbFileType()
        fileTypeInfo = svcdbFileType.getFileTypeInfo(params['attacheFile'].file_type_id)

        # ファイルの参照を記録する
        pkgSvcdbLog = PkgSvcdbLog()
        pkgSvcdbLog.saveOperationLog(
            current_user.tuid,
            db_id,
            operation_cd=Const.OPERATION_CD_SHOW_FILE,
            object_id=file_id,
            object_type='FILE',
            note=""
        )
        db.session.commit();

    except Exception as e:
        db.session.rollback()
        tb = sys.exc_info()[2]
        print("##########error_msg:" + str(e.with_traceback(tb)))

    res = make_response(
        send_file(
            params['df'],
            attachment_filename=params['attacheFile'].file_name, as_attachment=True
        )
    )
    res.headers['Content-Type'] = 'application/octet-stream'
    return res


def format_file_log_note(op_object, file_info, log_note_format):
    note = log_note_format
    if log_note_format is not None:
        log_format_arr = re.findall(r'[A-Za-z_0-9]+', log_note_format)
        for col in log_format_arr:
            col_name = col.lower()
            value = ''
            if hasattr(op_object, col_name):
                value = op_object.__dict__[col_name]
            elif hasattr(file_info, col_name):
                value = file_info.__dict__[col_name]
            note = note.replace('<#' + col + '#>', value)
    return note
