import os
import re
import sys

from flask import render_template, jsonify, current_app, make_response, send_file
from flask_login import current_user

from app import db
from app.controllers.package import PkgCmsLog
from app.lib.cms_lib.file_util import FileUtil
from app.lib.cms_lib.str_util import StrUtil
from app.lib.conf.const import Const
from app.models.cms.cms_file import CmsFile
from app.models.cms.cms_file_type import CmsFileType
from app.models.cms.cms_file_wk import CmsFileWk
from app.models.cms.cms_object import CmsObject


def file_link(db_id, object_id, file_type_id):
    if len(object_id) == 0:
        return render_template('error/404.html')

    cmsFile = CmsFile()
    attacheFileList = cmsFile.get_file_list(object_id, file_type_id).fetchall()
    if len(attacheFileList) > 1 or not attacheFileList:
        return render_template(
            'files_jqmodal.html',
            jqmTitle='添付ファイル画面',
            db_id=db_id,
            const=Const,
            appVer=current_app.config['APP_VER'],
            attacheFileList=attacheFileList)
    else:
        return download_file(db_id, attacheFileList[0].file_id, None, None)


def ctx_allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Const.CTX_FILE_ALLOWED_EXTENSIONS


def decompress_file(params):
    params['df'] = None
    if params['disp_mode'] == 'edit':
        cmsFileWkE = CmsFileWk()
        attacheFile = cmsFileWkE.getFile(params['edit_id'], params['file_id'])
    else:
        cmsFileE = CmsFile()
        attacheFile = cmsFileE.getFile(params['file_id'])
    if attacheFile is not None:
        try:
            file_path = os.path.join(attacheFile.dir_name, attacheFile.c_file_name)
            unzip_dir_path = str(StrUtil.get_safe_config(current_app, 'DOWNLOAD_DIR_PATH'))
            unzip_file_path = FileUtil.unzip_file(file_path, unzip_dir_path, attacheFile.file_id)

            params['attacheFile'] = attacheFile
            params['df'] = unzip_file_path
        except FileNotFoundError:
            StrUtil.print_error("FileNotFoundError")

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
        cmsFileType = CmsFileType()
        fileTypeInfo = cmsFileType.getFileTypeInfo(params['attacheFile'].file_type_id)
        cmsObject = CmsObject()
        opObject = cmsObject.getCmsObject(params['attacheFile'].parent_object_id)
        # ファイルの参照を記録する
        pkgCmsLog = PkgCmsLog()
        pkgCmsLog.saveOperationLog(
            current_user.tuid,
            db_id,
            operation_cd=Const.OPERATION_CD_SHOW_FILE,
            object_id=file_id,
            object_type='FILE',
            note=format_file_log_note(opObject, params['attacheFile'], fileTypeInfo.log_notes_format)
        )
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        tb = sys.exc_info()[2]
        StrUtil.print_error("download_file. error_msg:{}".format(str(e.with_traceback(tb))))

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
                value = getattr(op_object, col_name)
            elif hasattr(file_info, col_name):
                value = getattr(file_info, col_name)
            note = note.replace('<#' + col + '#>', value)
    return note
