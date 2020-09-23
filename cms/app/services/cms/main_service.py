import json

from flask import render_template, current_app, Response, url_for, flash
from flask_login import current_user
from werkzeug.utils import redirect

import app.lib.cms_lib.session
from app import db
from app.controllers.package import PkgCmsSecurity, PkgCmsLog
from app.lib.cms_lib.ctx_util import CtxUtil
from app.lib.cms_lib.date_util import DateUtil
from app.lib.cms_lib.session import session
from app.lib.cms_lib.str_util import StrUtil
from app.lib.conf.const import Const
from app.models.cms_admin.cms_ctx_data import CmsCtxData
from app.models.cms.cms_folder import CmsFolder
from app.models.cms_admin.cms_keyword_master import CmsKeywordMaster
from app.models.cms_admin.cms_keyword_setting import CmsKeywordSetting
from app.models.cms.cms_object import CmsObject
from app.models.cms.cms_object_keyword import CmsObjectKeyword
from app.models.cms_db_admin.cms_object_property import CmsObjectProperty
from app.models.cms_db_admin.cms_object_prop_selection_list import CmsObjectPropSelectionList
from app.models.cms.cms_tree_view_setting import CmsTreeViewSetting
from app.models.cms_db_admin.cms_search_setting import CmsSearchSetting
from app.models.cms_admin.cms_style_master import CmsStyleMaster


def main_init(db_id, request):
    if len(db_id) == 0:
        return render_template('error/404.html')

    db_name = ""
    information_message = ""
    # TODO result_cnt
    result_cnt = 0

    if app.lib.cms_lib.session.current_db:
        db_name = app.lib.cms_lib.session.current_db.db_name
        information_message = app.lib.cms_lib.session.current_db.information_message
        StrUtil.print_debug('main_init. db_name:{0} information_message:{1}'.format(
            db_name, information_message))

    db_id = app.lib.cms_lib.session.current_db.db_id
    cmsSecurity = PkgCmsSecurity()
    is_db_editable = cmsSecurity.isDbEditable(db_id, current_user.get_id())

    # タブ情報を取得
    viewType = request.args.get('view_type')
    cmsTreeViewSetting = CmsTreeViewSetting()
    tabList = cmsTreeViewSetting.getTreeViewSettingList(db_id)
    if viewType is None or len(viewType) <= 0:
        treeSetting = cmsTreeViewSetting.getTreeViewSettingList(db_id).first()
        viewType = treeSetting.view_type
        treeOpenFlg = treeSetting.tree_open_flg
    else:
        treeSetting = cmsTreeViewSetting.getTreeViewSetting(db_id, viewType)
        treeOpenFlg = treeSetting.tree_open_flg

    jtree_store = ''
    selected_node_id = ''
    if request.method == 'GET':
        jtree_store = request.args.get('jtree_store') or ''
        selected_node_id = request.args.get('selected_node_id') or ''

    # 通常検索機能
    searchSetting = CmsSearchSetting().getSearchSettingByDbId(db_id)

    # 画面表示用CSS STYLEを取得
    colorSettingDic = CmsStyleMaster().getStyleSettings(db_id, Const.STYLE_TYPE_COLOR)

    return render_template(
        'main.html',
        title=db_name,
        view_type=viewType,
        tree_open_flg=treeOpenFlg,
        db_id=db_id,
        db_name=db_name,
        information_message=information_message,
        result_cnt=result_cnt,
        current_user=current_user,
        jtree_store=jtree_store,
        selected_node_id=selected_node_id,
        is_edit_mode=StrUtil.get_safe_edit_mode(str(db_id) + '_is_edit_mode', session),
        is_db_editable=is_db_editable,
        tabList=tabList,
        searchSetting=searchSetting,
        colorSettingDic=colorSettingDic,
        appVer=current_app.config['APP_VER'],
        is_db_admin_user=isDbAdminUser(str(db_id), str(current_user.get_id())),
    )


# 管理者権限チェック
def isDbAdminUser(db_id, user_id):
    cmsSecurity = PkgCmsSecurity()
    return cmsSecurity.isDbAdminUser(db_id, user_id)


def swhEditMode():
    db_id = app.lib.cms_lib.session.get_db_id()
    if db_id + '_is_edit_mode' in session:
        if StrUtil.get_safe_edit_mode(str(db_id) + '_is_edit_mode', session):
            session[str(db_id) + '_is_edit_mode'] = False
        else:
            cmsSecurity = PkgCmsSecurity()
            if cmsSecurity.isDbEditable(db_id, current_user.get_id()) == False:
                return render_template('error/noPrivs.html', errorMsg='編集権限がありません。')

            session[str(db_id) + '_is_edit_mode'] = True
    else:
        session[str(db_id) + '_is_edit_mode'] = False

    return redirect(url_for('index', db_id=db_id, jtree_store='keep'))


def getFolderList(db_id, request):
    folder_id = request.form.get("id")
    if (len(db_id) <= 0 or len(folder_id) <= 0):
        return render_template('error/404.html')

    show_obj_cnt_flg = int(request.form.get("show_obj_cnt_flg"))
    cmsFolder = CmsFolder()
    folder_id = folder_id.split("_")[0]
    if (folder_id == "#"):
        folder_id = cmsFolder.getRootFolderId(db_id)

    folderList = []
    if folder_id:
        # DBからフォルダ情報取得
        folderList = cmsFolder.getFolderListForJson(db_id, folder_id, show_obj_cnt_flg)

    return Response(json.dumps(folderList))


# ファイルリストを取得する
def get_file_list_json(db_id, view_type, id, sort_type, sort_column, sort_column_type):
    res, msg, header, fileList, sort = {}, "OK", [], [], []
    if len(db_id) <= 0 or len(id) <= 0:
        return render_template('error/404.html')

    fileList = []
    if 'KEYWORD' == view_type:
        keyword_id = id
        kwSetting = CmsKeywordSetting().getCmsKeywordSettingByKeywordId(db_id, keyword_id)
        format_id = kwSetting.format_id
        # ヘッダカラム取得
        header = CmsObjectProperty().getObjectPropertiesByFormatId(format_id)
        # リストソート情報取得
        sort = CmsObjectProperty().getObjectSortPropertiesByFormatId(format_id)
        # ファイルリスト取得
        objectIdList = CmsObjectKeyword().getObjectIdList(keyword_id)
        if len(objectIdList) > 0:
            fileList = CmsObject().getObjectListKeyword(objectIdList, header, sort)
    else:
        ids = id.split("_")
        folder_id = ids[0]
        format_id = ids[1]

        # フォルダ情報を取得
        folder = CmsFolder().getFolder(folder_id)
        # ヘッダカラム取得
        header = CmsObjectProperty().getObjectPropertiesByFormatId(format_id)
        # リストソート情報取得
        if sort_column is not None and len(sort_column) > 0:
            dic, sort = {}, []
            dic = {**dic, **{"db_column_name": sort_column}}
            dic = {**dic, **{"sort_key_order": sort_type}}
            dic = {**dic, **{"property_type": sort_column_type}}
            sort.append(dic)
        else:
            sort = CmsObjectProperty().getObjectSortPropertiesByFormatId(format_id)
        # ファイルリスト取得
        fileList = CmsObject().getObjectListInfo(folder_id, header, sort)
        # タイトル取得
        informationMessage = CmsFolder().getInformationMessage(folder_id)
        res = {**res, **{"informationMessage": informationMessage}}
        res = {**res, **{"child_object_type_id": str(folder.child_object_type_id)}}
        res = {**res, **{"folder_information_message": folder.information_message}}

    res = {**res, **{"msg": msg}}
    res = {**res, **{"header": header}}
    res = {**res, **{"dataList": fileList}}
    res = {**res, **{"id": id}}
    res = {**res, **{"sort_column": sort_column}}
    res = {**res, **{"sort_type": sort_type}}

    return Response(json.dumps(res, default=DateUtil.json_serial))


def getKeywordList(db_id, request):
    if len(db_id) <= 0:
        return render_template('error/404.html')

    keyword_mst_id = None
    if request.form.get("keyword_mst_id") is not None:
        keyword_mst_id = request.form.get("keyword_mst_id")

    # [1]の場合、オブジェクト数を表示する
    show_obj_cnt_flg = int(request.args.get('show_obj_cnt_flg', 0))

    # DBからキーワード情報取得
    cmsKeywordSetting = CmsKeywordSetting()
    keywordList = cmsKeywordSetting.getKeywordSettingListForJson(db_id, keyword_mst_id)

    cmsKeywordMaster = CmsKeywordMaster()
    childKeywordList = []
    for setting in keywordList:
        newKeywordList = cmsKeywordMaster.getKeywordListForJson(
            setting.get('id'), setting.get('separator'), show_obj_cnt_flg)
        childKeywordList[len(childKeywordList):len(childKeywordList)] = newKeywordList

    keywordList[len(keywordList):len(keywordList)] = childKeywordList
    return Response(json.dumps(keywordList))


def showCtxSearchList(db_id, request):
    if len(db_id) == 0:
        return render_template('error/404.html')

    db_name = ""
    result_cnt = 0

    if app.lib.cms_lib.session.current_db:
        db_name = app.lib.cms_lib.session.current_db.db_name

    # 全文検索テキストを取得する
    if request.method == 'GET':
        ctx_search_text = request.args.get('ctx_search_text')

    if request.method == 'POST':
        ctx_search_text = request.form['ctx_search_text']

    if not ctx_search_text:
        if request.method == 'POST':
            flash('検索条件を入れてください')
        ctx_search_list = None
        ctx_search_text = ''
    elif StrUtil.lenb(ctx_search_text) > 256 and request.method == 'POST':
        flash('検索条件が長すぎます')
        ctx_search_list = None
    else:
        # 全文検索リストを取得
        cmsCtxData = CmsCtxData()
        ctx_cond = CtxUtil.process_ctx_search_text(ctx_search_text)

        result_cnt = cmsCtxData.getCtxSearchListCnt(db_id, ctx_cond)
        ctx_search_list = cmsCtxData.getCtxSearchList(db_id, ctx_cond)

        note = ctx_search_text
        if len(note) > 100:
            note = ctx_search_text[0:100]

        # 全文検索を記録する
        pkgCmsLog = PkgCmsLog()
        pkgCmsLog.saveOperationLog(
            current_user.tuid,
            db_id,
            operation_cd=Const.OPERATION_CD_CTX_SEARCH,
            note='SearchCond: {}, ResultCnt: {}'.format(note, result_cnt)
        )
        db.session.commit()

    user_name = ''
    if current_user.is_active:
        user_name = current_user.get_user_name()

    return render_template(
        'ctx_search.html',
        db_id=db_id,
        db_name=db_name,
        result_cnt=result_cnt,
        user_name=user_name,
        ctx_search_text=ctx_search_text,
        ctx_search_list=ctx_search_list,
        appVer=current_app.config['APP_VER'])


# 検索条件を表示する
def open_search_jqmodal(request):
    search_setting_id = request.args.get('search_setting_id')
    if len(search_setting_id) == 0:
        return render_template('error/404.html')

    # 検索ダイアログの設定を取得
    searchSetting = CmsSearchSetting().getSearchSetting(search_setting_id)
    # 検索条件に表示する項目を取得
    proList = CmsObjectProperty().getObjectPropertiesByFormatId(searchSetting.search_dlg_format_id)
    # SELECTマスタ情報取得
    selectionMstDic = CmsObjectPropSelectionList().getSelectionMstDic(proList)

    return render_template(
        'search_jqmodal.html',
        jqmTitle=searchSetting.search_menu_title,
        searchSetting=searchSetting,
        selectionMstDic=selectionMstDic,
        proList=proList)


# 検索を実施する
def do_search(request):
    search_setting_id = request.args.get("search_setting_id")
    if len(search_setting_id) <= 0:
        return render_template('error/404.html')

    res, msg, condList, resProList, fileList, sort = {}, "OK", [], [], [], []
    searchSetting = CmsSearchSetting().getSearchSetting(search_setting_id)
    # 検索条件プロパティリスト取得
    condProList = CmsObjectProperty().getObjectPropertiesByFormatId(searchSetting.search_dlg_format_id)
    # リストソート情報取得
    sort = CmsObjectProperty().getObjectSortPropertiesByFormatId(searchSetting.search_dlg_format_id)
    # 検索結果プロパティリスト取得
    resProList = CmsObjectProperty().getObjectPropertiesByFormatId(searchSetting.result_format_id)

    for pro in condProList:
        val, startVal, endVal = '', '', ''
        if "DATE" == pro.get("property_type"):
            startVal = request.args.get(pro.get("db_column_name").lower() + Const.START)
            endVal = request.args.get(pro.get("db_column_name").lower() + Const.END)
        else:
            val = request.args.get(pro.get("db_column_name").lower())
        if (val is not None and len(val) > 0) or ((startVal is not None and len(startVal) > 0) or (endVal is not None and len(endVal) > 0)):
            strTemp = ""
            if "DATE" != pro.get("property_type"):
                strTemp += "AND O." + pro.get("db_column_name")

            if "TEXT" == pro.get("property_type"):
                strTemp += " LIKE '%" + val + "%'"
            elif "DATE" == pro.get("property_type"):
                if startVal is not None and len(startVal) > 0:
                    strTemp += "AND TRUNC(O." + pro.get("db_column_name") + ")"
                    strTemp += " >= TO_DATE('" + startVal + "', 'YYYY/MM/DD') "
                if endVal is not None and len(endVal) > 0:
                    strTemp += "AND TRUNC(O." + pro.get("db_column_name") + ")"
                    strTemp += " <= TO_DATE('" + endVal + "', 'YYYY/MM/DD') "
            else:
                strTemp += " = '" + val + "'"
            condList.append(strTemp)

    # ファイルリスト取得
    fileList = CmsObject().searchObjectList(condList, resProList, sort)

    res = {**res, **{"search_type": "COND_SEARCH"}}
    res = {**res, **{"msg": msg}}
    res = {**res, **{"header": resProList}}
    res = {**res, **{"dataList": fileList}}
    res = {**res, **{"search_setting_id": search_setting_id}}
    return Response(json.dumps(res))
