import gzip
import os
import re
import sys
from datetime import datetime
import pandas as pd
from flask import render_template, jsonify, current_app, session
from flask_login import current_user

import app.lib.cms_lib.session
from app import db
from app.controllers.package import PkgCmsSecurity, PkgCmsLog
from app.forms.property_form import PropertyForm
from app.lib.cms_lib.db_util import DbUtil
from app.lib.cms_lib.file_util import FileUtil
from app.lib.cms_lib.str_util import StrUtil
from app.lib.conf.const import Const
from app.models.cms_common import CmsCommon
from app.models.cms_ctx_data import CmsCtxData
from app.models.cms_file import CmsFile
from app.models.cms_file_type import CmsFileType
from app.models.cms_file_wk import CmsFileWk
from app.models.cms_list_format import CmsListFormat
from app.models.cms_object import CmsObject
from app.models.cms_object_keyword import CmsObjectKeyword
from app.models.cms_object_prop_selection_list import CmsObjectPropSelectionList
from app.models.cms_object_property import CmsObjectProperty
from app.models.cms_object_type import CmsObjectType
from app.models.cms_tree_view_setting import CmsTreeViewSetting
from app.models.cms_folder import CmsFolder


def property(func, request):
    cmsSecurity = PkgCmsSecurity()
    db_id = app.lib.cms_lib.session.get_db_id()
    if not db_id or (
            ('edit' == func or 'new' == func) and cmsSecurity.isDbEditable(db_id, current_user.get_id()) is False):
        return render_template('error/noPrivs.html', errorMsg='編集権限がありません。')

    object_id = request.args.get('object_id')
    ids = request.args.get('id')
    idArray = ids.split("_")
    folder_id = idArray[0]
    display_order = request.args.get('displayOrder')

    cmsFolder = CmsFolder()
    folder = cmsFolder.getFolder(folder_id)
    folderTxt = cmsFolder.getFolderTxt(db_id, display_order, folder_id)

    form = PropertyForm()
    form.db_id.data = db_id
    form.ids.data = ids
    ids_org = request.args.get('id_org')
    if ids_org is not None and len(ids_org) > 0:
        form.ids_org.data = ids_org
    else:
        form.ids_org.data = ids
    form.folder_id.data = folder_id

    file_edit_id = None
    if 'edit' == func or 'new' == func:
        format_id = folder.form_format_id
        cmsCommon = CmsCommon()
        file_edit_id = cmsCommon.getObjectIdSeq()

        if 'new' == func:
            object_id = str(cmsCommon.getObjectIdSeq())
        elif 'edit' == func:
            # ワーク表データ初期化
            cmsFileWk = CmsFileWk()
            cmsFileWk.intFileDatas(file_edit_id, object_id)
            db.session.commit()
        page_name = 'cms/property_edit.html'
    else:
        format_id = folder.property_format_id
        page_name = 'cms/property_detail.html'

    form.object_id.data = object_id if object_id is not None else ''
    if format_id is None or len(str(format_id)) == 0:
        return render_template('error/404.html')

    cmsListFormat = CmsListFormat()
    cmsObject = CmsObject()
    cmsObjectProperty = CmsObjectProperty()
    cmsFileType = CmsFileType()

    # ヘッダカラム取得
    listFormat = cmsListFormat.getCmsListFormat(format_id)
    form.object_type_id.data = str(listFormat.object_type_id)

    proList = cmsObjectProperty.getObjectPropertiesByFormatId(format_id)
    # SELECTマスタ情報取得
    selection_mst_dic = CmsObjectPropSelectionList().getSelectionMstDic(proList)
    fileTypeList = cmsFileType.getFileTypeList(listFormat.object_type_id, func)

    proValues = {}
    if object_id is not None and len(object_id) > 0:
        proValues = cmsObject.getPropertyObjectValues(object_id, proList)

    loadKeywordTreeFlg = False
    reloadContentsFlg = False
    index = 0
    title = ''
    for pro in proList:
        if "KEYWORD" == pro.get("property_type"):
            value = proValues.get('keyword_id_text_' + str(index))
            loadKeywordTreeFlg = True
        else:
            value = proValues.get('col_' + str(index))

        if index == 0:
            title = value
        getattr(form, pro.get("db_column_name").lower()).data = value if value != None else ''
        index += 1

    # ファイルタイプ毎にファイルリストを取得
    if 'edit' == func or 'new' == func:
        fileTypeDic = getWkFileTypeDic(file_edit_id, object_id, fileTypeList)
    else:
        fileTypeDic = getFileTypeDic(object_id, fileTypeList)

    return render_template(
        page_name,
        title=app.lib.cms_lib.session.current_db.db_name + '-' + str(title or ''),
        current_user=current_user,
        func=func,
        form=form,
        db_name=app.lib.cms_lib.session.current_db.db_name,
        proList=proList,
        is_edit_mode=StrUtil.get_safe_edit_mode(str(db_id) + '_is_edit_mode', session),
        max_upload_file_size=FileUtil.get_max_upload_file_size(),
        proValues=proValues,
        fileTypeList=fileTypeList,
        fileTypeDic=fileTypeDic,
        selectionMstDic=selection_mst_dic,
        file_edit_id=file_edit_id,
        loadKeywordTreeFlg=loadKeywordTreeFlg,
        reloadContentsFlg=reloadContentsFlg,
        tabName=folderTxt.tab_name,
        folderPath=folderTxt.folder_path,
        displayOrder=display_order)


def property_save(db_id, func, request):
    form = PropertyForm()

    err_msgs = []
    isSaveError = False
    reloadContentsFlg = False
    cmsObject = CmsObject()
    cmsFileType = CmsFileType()
    cmsObjectType = CmsObjectType()
    cmsObjectProperty = CmsObjectProperty()

    # フォルダ情報を取得
    folder = CmsFolder().getFolder(form.folder_id.data)
    folderTxt = CmsFolder().getFolderTxt(db_id, request.form.get('displayOrder'), form.folder_id.data)
    format_id = folder.form_format_id
    # プロパティリストを取得
    proList = cmsObjectProperty.getObjectPropertiesByFormatId(format_id)
    file_edit_id = request.form.get('file_edit_id')

    # 入力チェックする
    param_prop = {'err_msgs': [], 'form': form, 'pro_list': proList}
    DbUtil.check_input_form_data_by_prop(param_prop)

    if len(param_prop['err_msgs']) > 0:
        err_msgs = param_prop['err_msgs']
        isSaveError = True

    if form.validate_on_submit() is False:
        StrUtil.print_debug('property_save validate error.')
        isSaveError = True
    elif not isSaveError:
        try:
            objectType = cmsObjectType.getCmsObjectType(db_id, form.object_type_id.data)

            # db.session.begin()
            # 新規の場合
            if 'new' == func:
                insObject = CmsObject()
                insObject.db_id = int(db_id)
                insObject.parent_folder_id = int(form.folder_id.data)
                insObject.object_type_id = int(form.object_type_id.data)
                insObject.object_id = int(form.object_id.data)
                for pro in proList:
                    if "KEYWORD" == pro.get("property_type"):
                        continue

                    col_name = pro.get("db_column_name").lower()
                    value = getattr(form, col_name).data
                    if col_name.startswith("num_"):
                        if len(value) > 0:
                            value = int(value)
                        else:
                            value = None
                    setattr(insObject, col_name, value)
                cmsObject.addObject(insObject, current_user.get_id())

                # オブジェクトの新規登録を記録する
                pkgCmsLog = PkgCmsLog()
                pkgCmsLog.saveOperationLog(
                    current_user.tuid,
                    db_id,
                    operation_cd=Const.OPERATION_CD_CREATE_OBJECT,
                    object_id=insObject.object_id,
                    object_type='OBJECT',
                    note=format_object_log_note(form, objectType.log_notes_format)
                )
                opObject = insObject
            else:
                # 編集の場合
                uptObject = cmsObject.getCmsObject(form.object_id.data)

                if form.ids_org.data != form.ids.data:
                    uptObject = clearColValue(uptObject,
                                ['object_id', 'db_id', 'object_type_id', 'created_at', 'created_by', 'is_deleted'])

                for pro in proList:
                    col_name = pro.get("db_column_name").lower()
                    value = getattr(form, col_name).data
                    if col_name.startswith("num_"):
                        if len(value) > 0:
                            value = int(value)
                        else:
                            value = None

                    setattr(uptObject, col_name, value)

                # folder_idも変更可能
                uptObject.parent_folder_id = int(form.folder_id.data)
                uptObject.ctx_indexed_flg = 0
                uptObject.updated_by = current_user.get_id()
                uptObject.updated_at = datetime.now()

                # オブジェクトの変更を記録する
                pkgCmsLog = PkgCmsLog()
                pkgCmsLog.saveOperationLog(
                    current_user.tuid,
                    db_id,
                    operation_cd=Const.OPERATION_CD_UPDATE_OBJECT,
                    object_id=uptObject.object_id,
                    object_type='OBJECT',
                    note=format_object_log_note(form, objectType.log_notes_format)
                )
                opObject = uptObject

            # キーワードの保存
            cmsObjectKeyword = CmsObjectKeyword()
            cmsObjectKeyword.deleteObjectKeywordList(int(form.object_id.data))
            for pro in proList:
                if "KEYWORD" != pro.get("property_type"):
                    continue

                col_name = pro.get("db_column_name").lower()
                values = getattr(form, col_name).data.split(", ")

                for value in values:
                    if not value:
                        continue
                    keyword_id = value.split("#")[0]
                    StrUtil.print_debug('property_save keyword_id:{}'.format(str(keyword_id)))
                    objectKeyword = CmsObjectKeyword()
                    objectKeyword.object_id = int(form.object_id.data)
                    objectKeyword.db_column_name = pro.get("db_column_name")
                    objectKeyword.keyword_id = keyword_id
                    cmsObjectKeyword.addObjectKeyword(objectKeyword)

            # 添付ファイルの保存（CMS_FILE_WKテーブル⇒CMS_FILEテーブル）
            now = datetime.now()
            uploadDirPath = current_app.config['UPLOAD_DIR_PATH']
            uploadDirPath = os.path.join(uploadDirPath, now.strftime("%Y%m"))
            uploadDirPath = os.path.join(uploadDirPath, now.strftime("%Y%m%d"))
            uploadDirPath = os.path.join(uploadDirPath, db_id)
            uploadDirPath = os.path.join(uploadDirPath, form.object_id.data)
            if not os.path.exists(uploadDirPath):
                os.makedirs(uploadDirPath)

            cmsFile = CmsFile()
            cmsFileWk = CmsFileWk()
            cmsFileType = CmsFileType()
            fileTypeList = cmsFileType.getFileTypeList(int(form.object_type_id.data))
            for fileType in fileTypeList:
                fileList = cmsFileWk.getFileList(file_edit_id, int(form.object_id.data), fileType.file_type_id)
                fileTypeInfo = cmsFileType.getFileTypeInfo(fileType.file_type_id)
                for fileDataWk in fileList:
                    fileData = cmsFile.getFile(fileDataWk.file_id)
                    if fileData != None and fileData.file_id != None and fileDataWk.is_deleted == 1:
                        cmsFile.delFile(fileData.file_id, current_user.get_id())

                        # ファイルの削除を記録する
                        pkgCmsLog = PkgCmsLog()
                        pkgCmsLog.saveOperationLog(
                            current_user.tuid,
                            db_id,
                            operation_cd=Const.OPERATION_CD_DELETE_FILE,
                            object_id=fileData.file_id,
                            object_type='FILE',
                            note=format_file_log_note(opObject, fileData, fileTypeInfo.log_notes_format)
                        )

                    elif fileData == None and fileDataWk.is_deleted == 0:
                        cmsFileN = CmsFile()
                        cmsFileN.file_id = fileDataWk.file_id
                        cmsFileN.parent_object_id = fileDataWk.parent_object_id
                        cmsFileN.file_type_id = fileDataWk.file_type_id
                        cmsFileN.file_name = fileDataWk.file_name
                        cmsFileN.file_size = fileDataWk.file_size
                        cmsFileN.c_file_name = fileDataWk.c_file_name
                        cmsFileN.created_by = fileDataWk.created_by
                        cmsFileN.created_at = fileDataWk.created_at
                        cmsFileN.updated_by = fileDataWk.updated_by
                        cmsFileN.updated_at = fileDataWk.updated_at
                        cmsFileN.is_deleted = 0
                        cmsFileN.ctx_indexed_flg = 0

                        try:
                            tmpFile = gzip.open(os.path.join(fileDataWk.dir_name, fileDataWk.c_file_name), 'rb')
                            gzFile = gzip.open(os.path.join(uploadDirPath, fileDataWk.c_file_name), 'wb')
                            gzFile.write(tmpFile.read())
                            gzFile.close()
                            tmpFile.seek(0, os.SEEK_END)
                        except Exception as e:
                            db.session.rollback()
                            tb = sys.exc_info()[2]
                            StrUtil.print_error('property_save error_msg:{}'.format(str(e.with_traceback(tb))))
                            continue

                        cmsFileN.dir_name = uploadDirPath
                        cmsFileN.c_file_size = tmpFile.tell()
                        cmsFile.addFile(cmsFileN)

                        # ファイルの登録を記録する
                        pkgCmsLog = PkgCmsLog()
                        pkgCmsLog.saveOperationLog(
                            current_user.tuid,
                            db_id,
                            operation_cd=Const.OPERATION_CD_CREATE_FILE,
                            object_id=cmsFileN.file_id,
                            object_type='FILE',
                            note=format_file_log_note(opObject, cmsFileN, fileTypeInfo.log_notes_format)
                        )

            db.session.commit()

            # 複数回更新時、ゴミデータを防ぐため「CMS_FILE_WK」
            if 'edit' == func:
                cmsCommon = CmsCommon()
                file_edit_id = cmsCommon.getObjectIdSeq()
                cmsFileWk.intFileDatas(file_edit_id, form.object_id.data)
                db.session.commit()

            if 'new' == func:
                func = 'edit'

            # 保存成功の場合
            reloadContentsFlg = True

            # ids_org更新
            form.ids_org.data = form.ids.data
        except Exception as e:
            db.session.rollback()
            tb = sys.exc_info()[2]
            StrUtil.print_error('property_save error_msg:{}'.format(str(e.with_traceback(tb))))
            err_msgs.append('Property save failed.')
            isSaveError = True

    # SELECTマスタ情報取得
    selection_mst_dic = CmsObjectPropSelectionList().getSelectionMstDic(proList)
    # ファイルタイプリストを取得
    fileTypeList = cmsFileType.getFileTypeList(int(form.object_type_id.data))

    # ヘッダカラム取得
    proValues = {}
    object_id = form.object_id.data
    if object_id is not None and len(object_id) > 0:
        proValues = cmsObject.getPropertyObjectValues(form.object_id.data, proList)

    # ファイルタイプごとにファイルリストを取得
    fileTypeDic = getFileTypeDic(form.object_id.data, fileTypeList)

    title = ''
    page_name = 'cms/property_edit.html'
    if not isSaveError and '1' == request.form.get('act_type'):
        page_name = 'cms/property_detail.html'

    return render_template(
        page_name,
        title=title,
        err_msgs=err_msgs,
        current_user=current_user,
        func=func,
        form=form,
        db_name=app.lib.cms_lib.session.current_db.db_name,
        proList=proList,
        is_edit_mode=StrUtil.get_safe_edit_mode(str(db_id) + '_is_edit_mode', session),
        max_upload_file_size=FileUtil.get_max_upload_file_size(),
        proValues=proValues,
        fileTypeList=fileTypeList,
        fileTypeDic=fileTypeDic,
        selectionMstDic=selection_mst_dic,
        file_edit_id=file_edit_id,
        loadKeywordTreeFlg=request.form.get('loadKeywordTreeFlg'),
        reloadContentsFlg=reloadContentsFlg,
        tabName=folderTxt.tab_name,
        folderPath=folderTxt.folder_path)


def property_delete(request):
    rtn_hash = {}
    status, msg = 'OK', ''
    db_id = request.form.get('db_id')
    object_id = request.form.get('object_id')
    if object_id == None or len(object_id) <= 0:
        status = 'Error'
        msg = 'object_id is null.'

    if status == 'OK':
        try:
            cmsObject = CmsObject()
            object = cmsObject.getCmsObject(object_id)
            cmsObject.delObject(object_id, current_user.get_id())

            # 添付ファイルの削除
            cmsFile = CmsFile()
            cmsFile.delFiles(object_id, current_user.get_id())

            # 全文検索テーブルから削除
            cmsCtxData = CmsCtxData()
            cmsCtxData.delCmsCtxData(object_id, db_id)

            # オブジェクトの変更を記録する
            cmsObjectType = CmsObjectType()
            objectType = cmsObjectType.getCmsObjectType(db_id, object.object_type_id)
            pkgCmsLog = PkgCmsLog()
            pkgCmsLog.saveOperationLog(
                current_user.tuid,
                db_id,
                operation_cd=Const.OPERATION_CD_DELETE_OBJECT,
                object_id=object_id,
                object_type='OBJECT',
                note=format_object_log_note(object, objectType.log_notes_format)
            )

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            tb = sys.exc_info()[2]
            StrUtil.print_error('property_delete error_msg:{}'.format(str(e.with_traceback(tb))))
            msg = 'Property save failed.'
            status = 'Error'

    rtn_hash['msg'] = msg
    rtn_hash['status'] = status
    return jsonify(rtn_hash)


# ファイルアップロード
def file_upload(param):
    func = param["func"]
    msg = []
    rtn_hash = {}
    status = 'OK'
    flg = 0  # 重複フラグ
    if not check_file_allowed(param["file_names"], msg):
        status = 'Error'
    else:
        if 'check_overwrite' == func:
            if check_over_write(param['file_edit_id'], param["object_id"],
                                param["file_type_id"], param["file_names"], msg):
                flg = 1
                if msg and len(msg) > 0:
                    msg.append("<br />")
                msg.append('ファイルはすでに登録されました。上書きしますか？<br />')
            rtn_hash['check_overwrite_flg'] = flg

        elif 'file_upload_by_drop' == func:
            if not do_upload_file(param, msg):
                status = 'Error'

    rtn_hash['msg'] = "".join(map(str, msg))
    rtn_hash['status'] = status
    return jsonify(rtn_hash)


# ファイルアップロードする
def do_upload_file(param, msg):
    upload_files = param["file_paths"]
    file_type_id = param["file_type_id"]
    file_edit_id = param["file_edit_id"]

    count = 1
    del_file = []
    cmsCommon = CmsCommon()
    cmsFileWkE = CmsFileWk()
    try:
        # db.session.begin()
        af_obj = CmsFileWk(param["object_id"])
        af_obj.edit_id = file_edit_id
        af_obj.file_type_id = file_type_id

        uploadTmpDirPath = current_app.config['UPLOAD_TMP_DIR_PATH']
        uploadTmpDirPath = os.path.join(uploadTmpDirPath, app.lib.cms_lib.session.get_db_id())
        uploadTmpDirPath = os.path.join(uploadTmpDirPath, param["object_id"])
        if not os.path.exists(uploadTmpDirPath):
            os.makedirs(uploadTmpDirPath)

        for file in upload_files:
            cmsFileWk = CmsFileWk(param["object_id"])
            fileName = file.filename
            if fileName is None or '' == fileName:
                return "EMPTY_FILE_ERROR"

            if not allowed_file(fileName):
                return "NOT_ALLOWED_FILE"

            af_obj.file_name = fileName
            # 上書きの場合、元のファイルを削除する
            if cmsFileWkE.chkExistsFile(af_obj):
                del_file.append(af_obj.file_id)

            fileId = cmsCommon.getObjectIdSeq()
            cFileName = '%d.gz' % fileId
            StrUtil.print_debug('do_upload_file file_name:{}'.format(os.path.join(uploadTmpDirPath, cFileName)))
            f = gzip.open(os.path.join(uploadTmpDirPath, cFileName), 'wb')
            f.write(file.read())
            f.close()
            file.seek(0, os.SEEK_END)

            cmsFileWk.edit_id = file_edit_id
            cmsFileWk.file_id = fileId
            cmsFileWk.file_type_id = file_type_id
            cmsFileWk.file_name = fileName
            cmsFileWk.file_size = file.tell()
            cmsFileWk.dir_name = uploadTmpDirPath
            cmsFileWk.c_file_name = cFileName
            cmsFileWk.c_file_size = os.stat(os.path.join(uploadTmpDirPath, cFileName)).st_size
            cmsFileWkE.addFile(cmsFileWk, current_user.tuid)
            count += 1

        # 上書き対象ファイルを削除する
        if len(del_file) > 0:
            for del_file_id in del_file:
                cmsFileWkE.delFile(file_edit_id, del_file_id, current_user.get_id())

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        tb = sys.exc_info()[2]
        StrUtil.print_error('do_upload_file error_msg:{}'.format(str(e.with_traceback(tb))))
        msg.append(e.with_traceback(tb))
        return False
    return True


# アップロードできる種類かチェック
def check_file_allowed(file_names, msg):
    chk_rst = True

    for file_name in file_names:
        if not allowed_file(file_name):
            if msg and len(msg) > 0:
                msg.append("<br />")
            msg.append(Const.NOT_FILE_ALLOWED_MSG.format(file_name))
            chk_rst = False
    return chk_rst


# ファイル存在チェック
def check_over_write(file_edit_id, object_id, file_type_id, file_names, msg):
    cmsFileWk = CmsFileWk()
    chk_rst = False

    cmsFileWk.get_file_list(file_edit_id, object_id, file_type_id)
    af_obj = CmsFileWk()
    af_obj.edit_id = file_edit_id
    af_obj.parent_object_id = object_id
    af_obj.file_type_id = file_type_id
    for file_name in file_names:
        af_obj.file_name = file_name
        existsAttachedFile = cmsFileWk.getExistsFile(af_obj)
        if existsAttachedFile and existsAttachedFile.file_id != '':
            if msg and len(msg) > 0:
                msg.append("<br />")
            msg.append(file_name)
            chk_rst = True
    return chk_rst


def prop_delete_file(request):
    rtn_hash = {}
    status, msg = 'OK', ''
    try:
        cmsFileWk = CmsFileWk()
        cmsFileWk.delFile(request.form.get('file_edit_id'), request.form.get('file_id'), current_user.get_id())
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        tb = sys.exc_info()[2]
        StrUtil.print_error('prop_delete_file error_msg:{}'.format(str(e.with_traceback(tb))))
        msg = e.with_traceback(tb)
        status = 'Error'

    rtn_hash['msg'] = msg
    rtn_hash['status'] = status
    rtn_hash['file_type_id'] = request.form.get('file_type_id')
    rtn_hash['func'] = 'prop_delete_file'
    return jsonify(rtn_hash)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Const.FILE_ALLOWED_EXTENSIONS


def getFileTypeDic(object_id, fileTypeList):
    cmsFile = CmsFile()
    fileTypeDic = {}
    for fileType in fileTypeList:
        fileList = []
        if object_id is not None and len(object_id) > 0:
            fileList = cmsFile.get_file_list(object_id, fileType.file_type_id)
        fileTypeDic[fileType.file_type_id] = fileList

    return fileTypeDic


def getWkFileTypeDic(file_edit_id, object_id, fileTypeList):
    cmsFileWk = CmsFileWk()
    fileTypeDic = {}
    for fileType in fileTypeList:
        fileList = []
        if object_id != None and len(object_id) > 0:
            fileList = cmsFileWk.get_file_list(file_edit_id, object_id, fileType.file_type_id)
        fileTypeDic[fileType.file_type_id] = fileList

    return fileTypeDic


def get_files(file_edit_id, object_id, file_type_id):
    dic, array, cmsFileWk = {}, [], CmsFileWk()
    for rowproxy in cmsFileWk.get_file_list_for_json(file_edit_id, object_id, file_type_id):
        for column, val in rowproxy.items():
            dic = {**dic, **{column: val}}
        array.append(dic)
    return array


def open_folder_tree(request):
    db_id = request.args.get('db_id')
    folder_id = request.args.get('folder_id')
    if len(db_id) == 0 or len(folder_id) == 0:
        return render_template('error/404.html')

    folder = CmsFolder().getFolder(folder_id)
    treeSetting = CmsTreeViewSetting().getTreeViewSetting(db_id, Const.FOLDER)
    return render_template(
        'cms/folder_tree_jqmodal.html',
        jqmTitle='Folders',
        db_id=db_id,
        folder_id=folder_id,
        selected_node_id=str(folder.folder_id) + "_" + str(folder.list_format_id),
        treeOpenFlg=treeSetting.tree_open_flg)


def format_object_log_note(op_object, log_note_format):
    note = log_note_format
    if log_note_format is not None:
        log_format_arr = re.findall(r'[A-Za-z_0-9]+', log_note_format)
        for col in log_format_arr:
            col_name = col.lower()
            value = ''
            if isinstance(op_object, PropertyForm) and hasattr(op_object, col_name):
                value = getattr(op_object, col_name).data
            elif isinstance(op_object, CmsObject) and hasattr(op_object, col_name):
                value = getattr(op_object, col_name)
            elif isinstance(op_object, pd.DataFrame) and (col_name in op_object.index):
                value = op_object.at[col_name, "property_name"]
            note = note.replace('<#' + col + '#>', StrUtil.get_safe_string(value))
    return note


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
            note = note.replace('<#' + col + '#>', StrUtil.get_safe_string(value))
    return note


def clearColValue(cmsObject, skipCols):
    d = cmsObject.__dict__
    for key in d:
        if not key.startswith('_') and key not in skipCols:
            print(key)
            setattr(cmsObject, key, None)
    return cmsObject
