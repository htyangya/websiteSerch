import re
import sys

from flask import render_template, current_app, url_for, request
from flask_login import current_user
from werkzeug.utils import redirect

from app import db
from app.controllers.package import PkgCmsSecurity
from app.forms.cms_admin.database_form import DatabaseForm
from app.forms.cms_admin.ip_addr_form import IpAddrForm
from app.forms.cms_admin.keyword_form import KeywordForm
from app.forms.cms_admin.list_format_form import ListFormatForm
from app.forms.cms_admin.style_setting_form import StyleSettingForm
from app.lib.cms_lib.db_util import DbUtil
from app.lib.cms_lib.html_util import HtmlUtil
from app.lib.cms_lib.session import get_db_id
from app.lib.cms_lib.str_util import StrUtil
from app.lib.conf.const import Const
from app.models.cms_admin.cms_ip_addr_list import CmsIpAddrList
from app.models.cms_admin.cms_ip_addr_list_master import CmsIpAddrListMaster
from app.models.cms_admin.cms_keyword_master import CmsKeywordMaster
from app.models.cms_admin.cms_keyword_setting import CmsKeywordSetting
from app.models.cms_admin.cms_list_format import CmsListFormat
from app.models.cms_admin.cms_list_format_columns import CmsListFormatColumns
from app.models.cms_admin.cms_list_format_sort import CmsListFormatSort
from app.models.cms_admin.cms_style_master import CmsStyleMaster
from app.models.cms_admin.cms_style_setting import CmsStyleSetting
from app.models.cms_common import CmsCommon
from app.models.cms_db_admin.cms_db import CmsDb
from app.models.cms_db_admin.cms_object_prop_selection_mst import CmsObjectPropSelectionMst
from app.models.cms_db_admin.cms_object_property import CmsObjectProperty
from app.models.cms_db_admin.cms_object_type import CmsObjectType


def admin_main_init():
    # ナビゲーションリンク
    navi_arr_ref = []
    navi_arr_ref.append('Main Menu')
    navi_arr_ref.append(url_for('adm_index'))

    return render_template(
        'cms_admin/main.html',
        title='ログインメイン',
        navi_bar_html=HtmlUtil.print_navi_bar(navi_arr_ref),
        current_user=current_user,
        appVer=current_app.config['APP_VER'])


# Database management start
# データベースメニューへ遷移
def database_list():
    dbList = CmsDb().getCmsDbList()
    # ナビゲーションリンク
    navi_arr_ref = []
    navi_arr_ref.append('Main Menu')
    navi_arr_ref.append(url_for('adm_index'))
    navi_arr_ref.append('Database')

    return render_template(
        'cms_admin/database_admin.html',
        title='CMS：Database Management',
        navi_bar_html=HtmlUtil.print_navi_bar(navi_arr_ref),
        dbList=dbList,
        current_user=current_user,
        appVer=current_app.config['APP_VER'])


def service_database(func, request):
    if len(func) == 0:
        return render_template('error/404.html')

    db_id = None
    form = DatabaseForm()
    cmsDb = CmsDb()
    cmsKeywordSetting = CmsKeywordSetting()
    cmsKeywordMaster = CmsKeywordMaster()
    keywordList = []
    editMode = 'Detail'
    page_id = 'cms_admin/database_detail.html'
    err_msgs = []
    isSaveError = False

    # 詳細
    if func == 'database_detail':
        db_id = request.args.get("db_id")
        cmsDb = CmsDb.getCmsDbProperty(db_id)
        form.dbName.data = cmsDb["db_name"]

        # キーワード情報を取得
        keywordSettingList = cmsKeywordSetting.getKeywordSettingList(db_id)
        for keywordSetting in keywordSettingList:
            kwSetting = CmsKeywordSetting()
            kwSetting.keyword_mst_id = keywordSetting.keyword_mst_id
            kwSetting.keyword_name = keywordSetting.keyword_name
            kwSetting.tree_separator = keywordSetting.tree_separator
            if keywordSetting.multi_set_flg == 0:
                kwSetting.multiSetFlg = '1つ設定可能'
            elif keywordSetting.multi_set_flg == 1:
                kwSetting.multiSetFlg = '複数セット可能'
            if keywordSetting.not_null_flg == 1:
                kwSetting.notNullFlg = '必須'

            # キーワード
            kList = cmsKeywordMaster.getKeywordList(keywordSetting.keyword_mst_id)
            kwSetting.setKeywords(kList)
            keywordList.append(kwSetting)

    # 新規・編集
    elif func == 'database_edit':
        page_id = 'cms_admin/database_edit.html'
        db_id = request.args.get("db_id")
        # 新規の場合
        if db_id is None or len(db_id) == 0:
            cmsCommon = CmsCommon()
            form.dbId.data = cmsCommon.getObjectIdSeq()
            editMode = 'New'
        else:
            # 編集の場合
            form = getCmsDbForm(db_id)
            cmsDb = CmsDb.getCmsDbProperty(db_id)
            editMode = 'Edit'
    # 保存処理
    elif func == 'database_save':
        db_id = form.dbId.data
        # 入力チェックする
        cname = [
            form.dbId.label.text,
            form.dbName.label.text,
            form.sessionCookieName.label.text,
            form.displayOrder.label.text,
            form.loginMessage.label.text,
            form.informationMessage.label.text,
            form.remarks.label.text,
        ]
        input_value = [
            form.dbId.data,
            form.dbName.data,
            form.sessionCookieName.data,
            form.displayOrder.data,
            form.loginMessage.data,
            form.informationMessage.data,
            form.remarks.data,
        ]
        db_field = [
            form.dbId.label.text.upper(),
            form.dbName.label.text.upper(),
            form.sessionCookieName.label.text.upper(),
            form.displayOrder.label.text.upper(),
            form.loginMessage.label.text.upper(),
            form.informationMessage.label.text.upper(),
            form.remarks.label.text.upper(),
        ]
        col_prop = {'cname': cname, 'input_value': input_value, 'db_field': db_field}
        param_prop = {'err_msgs': [], 'table_name': 'CMS_DB', 'form': form, 'col_prop': col_prop}
        DbUtil.check_input_form_data_by_db(param_prop)

        if len(param_prop['err_msgs']) > 0:
            err_msgs = param_prop['err_msgs']
            isSaveError = True

        if request.method == 'POST':
            page_id = 'cms_admin/database_edit.html'
            editMode = request.form["editMode"]

        if request.method == 'POST' and not isSaveError:
            # form = DatabaseForm(request.form)
            if form.validate_on_submit() == False:
                StrUtil.print_debug('service_database validate error')
            else:
                try:
                    if 'New' == editMode:
                        cmsDb = getCmsDb(cmsDb, form)
                        CmsDb.addDb(cmsDb, current_user.get_id())
                        db.session.commit()
                        return redirect(url_for('database_admin'))
                    else:
                        cmsDb = CmsDb.getCmsDb(form.dbId.data)
                        cmsDb = getCmsDb(cmsDb, form)
                        db.session.commit()
                        return redirect(url_for('database', func='database_detail', db_id=form.dbId.data))
                except Exception as e:
                    db.session.rollback()
                    tb = sys.exc_info()[2]
                    StrUtil.print_error('error_msg:{}'.format(str(e.with_traceback(tb))))
                    err_msgs.append('Database save failed.')
    # 削除処理
    elif func == 'database_delete':
        db_id = request.form["db_id"]
        try:
            CmsDb.delDb(db_id, current_user.get_id())
            db.session.commit()
            return redirect(url_for('database_admin'))
        except Exception as e:
            db.session.rollback()
            tb = sys.exc_info()[2]
            StrUtil.print_error('error_msg:{}'.format(str(e.with_traceback(tb))))
            err_msgs.append('Database delete failed.')
            cmsDb = CmsDb.getCmsDbProperty(db_id)

    if editMode == 'New':
        title = 'CMS：Create Database'
        subTitle = 'Create Database'
    elif editMode == 'Edit':
        title = 'CMS：Modify Database'
        subTitle = 'Modify Database'
    else:
        title = 'CMS：' + cmsDb['db_name'] if 'db_name' in cmsDb else ''
        subTitle = ''

    # ナビゲーションリンク
    navi_arr_ref = []
    navi_arr_ref.append('Main Menu')
    navi_arr_ref.append(url_for('adm_index'))
    navi_arr_ref.append('Database')
    navi_arr_ref.append(url_for('database_admin'))
    if db_id is not None:
        navi_arr_ref.append(form.dbName.data)
        navi_arr_ref.append(url_for('database', func='database_detail', db_id=db_id))

    return render_template(
        page_id,
        title=title,
        navi_bar_html=HtmlUtil.print_navi_bar(navi_arr_ref),
        err_msgs=err_msgs,
        subTitle=subTitle,
        current_user=current_user,
        editMode=editMode,
        form=form,
        cmsDb=cmsDb,
        keywordList=keywordList,
        appVer=current_app.config['APP_VER'])


def delete_database_jqmodal(request):
    db_id = get_db_id()
    cmsDb = CmsDb.getCmsDb(db_id)

    return render_template(
        'cms_admin/delete_database_jqmodal.html',
        jqmTitle='Confirm',
        cmsDb=cmsDb)


def service_keyword(func, request):
    if len(func) == 0:
        return render_template('error/404.html')

    form = KeywordForm()
    editMode = 'Edit'
    page_id = 'cms_admin/keyword_edit.html'
    err_msgs = []
    isSaveError = False
    cmsKeywordSetting = CmsKeywordSetting()
    cmsKeywordMaster = CmsKeywordMaster()

    # 編集
    if func == 'keyword_edit':
        db_id = request.args.get("db_id")
        keyword_mst_id = request.args.get("keyword_mst_id")

        # DB情報の取得
        cmsDb = CmsDb.getCmsDb(db_id)
        form.dbId.data = db_id
        form.dbName.data = cmsDb.db_name

        # キーワードの設定
        keywordSettingList = cmsKeywordSetting.getKeywordSettingList(db_id, keyword_mst_id)
        for keywordSetting in keywordSettingList:
            form.keywordMstId.data = keyword_mst_id
            form.keywordName.data = keywordSetting.keyword_name
            form.multiSetFlg.data = str(keywordSetting.multi_set_flg)
            form.notNullFlg.data = str(keywordSetting.not_null_flg)
            form.treeSeparator.data = keywordSetting.tree_separator

            # キーワードマスタ
            kList = cmsKeywordMaster.getKeywordList(keywordSetting.keyword_mst_id)
            form.keywords.data = '\r\n'.join(kList)
    # 保存処理
    elif func == 'keyword_save':

        # 入力チェックする
        cname = [
            form.dbId.label.text,
            form.keywordMstId.label.text,
            form.keywordName.label.text,
            form.multiSetFlg.label.text,
            form.notNullFlg.label.text,
            form.treeSeparator.label.text,
        ]
        input_value = [
            form.dbId.data,
            form.keywordMstId.data,
            form.keywordName.data,
            form.multiSetFlg.data,
            form.notNullFlg.data,
            form.treeSeparator.data,
        ]
        db_field = [
            form.dbId.label.text.upper(),
            form.keywordMstId.label.text.upper(),
            form.keywordName.label.text.upper(),
            form.multiSetFlg.label.text.upper(),
            form.notNullFlg.label.text.upper(),
            form.treeSeparator.label.text.upper(),
        ]
        col_prop = {'cname': cname, 'input_value': input_value, 'db_field': db_field}
        param_prop = {'err_msgs': [], 'table_name': 'CMS_KEYWORD_SETTING', 'form': form, 'col_prop': col_prop}
        DbUtil.check_input_form_data_by_db(param_prop)

        # キーワード削除可能チェック
        usingKeywordList = cmsKeywordMaster.getUsingKeywordList(form.keywordMstId.data)
        keywordList = form.keywords.data.split('\r\n')
        for usingKeyword in usingKeywordList:
            if usingKeyword not in keywordList:
                param_prop['err_msgs'].append(Const.CANNOT_DELETE_USING_ITEM_ERR_MSG.format(usingKeyword))

        # エラー発生の場合
        if len(param_prop['err_msgs']) > 0:
            err_msgs = param_prop['err_msgs']
            isSaveError = True

        if request.method == 'POST' and not isSaveError:
            editMode = request.form["editMode"]
            # form = DatabaseForm(request.form)
            if form.validate_on_submit() == False:
                StrUtil.print_debug('validate error.')
            else:
                try:
                    # キーワードの設定テーブルの更新
                    keywordSetting = cmsKeywordSetting.getCmsKeywordSetting(form.keywordMstId.data)
                    keywordSetting.keyword_name = form.keywordName.data
                    keywordSetting.multi_set_flg = int(form.multiSetFlg.data)
                    keywordSetting.not_null_flg = int(form.notNullFlg.data)
                    keywordSetting.tree_separator = form.treeSeparator.data

                    # キーワードマスタの更新
                    cmsCommon = CmsCommon()
                    cmsKeywordMaster.deleteKeywords(form.keywordMstId.data)
                    display_order = 1
                    for keyword in keywordList:
                        if len(keyword) <= 0:
                            continue
                        if keyword in usingKeywordList:
                            # ソート順をリセットする
                            cmsKeywordMaster.updateUsingKeywordDisplayOrder(
                                form.keywordMstId.data, keyword, display_order)
                            display_order += 1
                            continue
                        ckm = CmsKeywordMaster()
                        ckm.keyword_mst_id = form.keywordMstId.data
                        ckm.keyword_id = cmsCommon.getObjectIdSeq()
                        ckm.keyword = keyword
                        ckm.display_order = display_order
                        cmsKeywordMaster.addKeywordMaster(ckm)
                        display_order += 1

                    db.session.commit()
                    return redirect(url_for('keyword_list', db_id=form.dbId.data))
                except Exception as e:
                    db.session.rollback()
                    tb = sys.exc_info()[2]
                    StrUtil.print_error('service_keyword error_msg:{}'.format(str(e.with_traceback(tb))))
                    err_msgs.append('Keyword save failed.')

    title = 'CMS：Update Keyword'
    subTitle = 'Update Keyword'

    # ナビゲーションリンク
    navi_arr_ref = []
    navi_arr_ref.append('Main Menu')
    navi_arr_ref.append(url_for('adm_index'))
    navi_arr_ref.append('Database')
    navi_arr_ref.append(url_for('database_admin'))
    navi_arr_ref.append(form.dbName.data)
    navi_arr_ref.append(url_for('database', func='database_detail', db_id=form.dbId.data))
    navi_arr_ref.append("Keyword")

    return render_template(
        page_id,
        title=title,
        navi_bar_html=HtmlUtil.print_navi_bar(navi_arr_ref),
        err_msgs=err_msgs,
        subTitle=subTitle,
        current_user=current_user,
        editMode=editMode,
        form=form,
        appVer=current_app.config['APP_VER'])


def getCmsDbForm(db_id):
    form = DatabaseForm()
    cmsDb = CmsDb.getCmsDb(db_id)
    form.dbId.data = cmsDb.db_id
    form.dbName.data = cmsDb.db_name
    form.sessionCookieName.data = cmsDb.session_cookie_name
    form.displayOrder.data = cmsDb.display_order
    form.loginMessage.data = cmsDb.login_message
    form.informationMessage.data = cmsDb.information_message
    form.remarks.data = cmsDb.remarks
    return form


def getCmsDb(cmsDb, form):
    cmsDb.db_id = form.dbId.data
    cmsDb.db_name = form.dbName.data
    cmsDb.session_cookie_name = form.sessionCookieName.data
    cmsDb.display_order = form.displayOrder.data
    cmsDb.login_message = form.loginMessage.data
    cmsDb.information_message = form.informationMessage.data
    cmsDb.remarks = form.remarks.data
    return cmsDb


# Database management end

# List/Property Format Start
# List Format リスト画面へ遷移
def list_format_list(request):
    db_id = request.args.get("db_id")
    cmsDb = CmsDb.getCmsDbProperty(db_id)
    format_type = 'LIST'
    page_id = 'cms_admin/list_format_list.html'
    title = 'CMS：List Format'
    sub_title = 'List Format'

    # ナビゲーションリンク
    navi_arr_ref = []
    navi_arr_ref.append('Main Menu')
    navi_arr_ref.append(url_for('adm_index'))
    navi_arr_ref.append('Database')
    navi_arr_ref.append(url_for('database_admin'))
    navi_arr_ref.append(cmsDb['db_name'])
    navi_arr_ref.append(url_for('database', func='database_detail', db_id=cmsDb['db_id']))
    navi_arr_ref.append(sub_title)

    cmsObjectType = CmsObjectType()
    objectTypeList = cmsObjectType.getObjectTypeList(db_id)
    cmsListFormat = CmsListFormat()
    objectTypeDic = {}
    listFormatDic = {}
    for objectType in objectTypeList:
        objectTypeDic[objectType.object_type_id] = objectType.object_type_name
        listFormatList = []
        if format_type is not None and len(format_type) > 0:
            listFormatList = cmsListFormat.getCmsListFormatList(objectType.object_type_id, format_type)
        listFormatDic[objectType.object_type_id] = listFormatList

    return render_template(
        page_id,
        title=title,
        navi_bar_html=HtmlUtil.print_navi_bar(navi_arr_ref),
        objectTypeDic=objectTypeDic,
        listFormatDic=listFormatDic,
        cmsDb=cmsDb,
        format_type=Const.LIST,
        current_user=current_user,
        appVer=current_app.config['APP_VER'])


# property_format リスト画面へ遷移
def property_format_list(request):
    db_id = request.args.get("db_id")
    cmsDb = CmsDb.getCmsDbProperty(db_id)
    page_id = 'cms_admin/property_format_list.html'
    format_type = 'PROPERTY'
    title = 'CMS：Property Format'
    sub_title = 'Property Format'

    # ナビゲーションリンク
    navi_arr_ref = []
    navi_arr_ref.append('Main Menu')
    navi_arr_ref.append(url_for('adm_index'))
    navi_arr_ref.append('Database')
    navi_arr_ref.append(url_for('database_admin'))
    navi_arr_ref.append(cmsDb['db_name'])
    navi_arr_ref.append(url_for('database', func='database_detail', db_id=cmsDb['db_id']))
    navi_arr_ref.append(sub_title)

    cmsObjectType = CmsObjectType()
    objectTypeList = cmsObjectType.getObjectTypeList(db_id)
    cmsListFormat = CmsListFormat()
    objectTypeDic = {}
    listFormatDic = {}
    for objectType in objectTypeList:
        objectTypeDic[objectType.object_type_id] = objectType.object_type_name
        listFormatList = []
        if format_type is not None and len(format_type) > 0:
            listFormatList = cmsListFormat.getCmsListFormatList(objectType.object_type_id, format_type)
        listFormatDic[objectType.object_type_id] = listFormatList

    return render_template(
        page_id,
        title=title,
        navi_bar_html=HtmlUtil.print_navi_bar(navi_arr_ref),
        objectTypeDic=objectTypeDic,
        listFormatDic=listFormatDic,
        cmsDb=cmsDb,
        format_type=Const.PROPERTY,
        current_user=current_user,
        appVer=current_app.config['APP_VER'])


# List/Property Formatの新規・更新・削除処理
def format_edit(func, db_id, format_type, object_type_id, format_id, request):
    if len(func) == 0:
        return render_template('error/404.html')
    form = ListFormatForm()
    form.objectTypeId.data = object_type_id
    editMode = 'Edit'
    page_id = 'cms_admin/list_format_edit.html'
    err_msgs = []
    isSaveError = False
    listFormatColumnsList = []
    listFormatSortList = []
    cmsListFormat = CmsListFormat()

    redirectUrl = 'list_format'
    if format_type == Const.PROPERTY:
        redirectUrl = 'property_format'
        page_id = 'cms_admin/property_format_edit.html'

    # propertyName情報の取得
    cmsDb = CmsDb.getCmsDb(db_id)
    cmsObjectProperty = CmsObjectProperty()
    dataList = cmsObjectProperty.getObjectPropertyNames(object_type_id)
    d, propertyNameList = {}, []
    for rowproxy in dataList:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        propertyNameList.append(d)

    # 新規・編集
    if func == 'edit':
        # 新規の場合
        if format_id is None or len(format_id) == 0:
            editMode = 'New'
            form.formatType.data = 'LIST'
            if format_type == Const.PROPERTY:
                form.formatType.data = 'PROPERTY'
        else:
            # 編集の場合
            form = getListFormatForm(format_id)
            listFormatColumnsList = CmsListFormatColumns().getCmsListFormatColumnsList(format_id)
            listFormatSortList = CmsListFormatSort().getCmsListFormatSortList(format_id)
            editMode = 'Edit'

    # 保存処理
    elif func == 'save':
        format_Id = ''
        formatIdList = request.form["formatIdList"]
        # cms_list_format.format_type = ‘LIST’の場合
        if format_type == Const.LIST:
            sort_key0 = request.form["sort_key0"]
            sort_key_order0 = request.form["sort_key_order0"]
            sort_key1 = request.form["sort_key1"]
            sort_key_order1 = request.form["sort_key_order1"]
            sort_key2 = request.form["sort_key2"]
            sort_key_order2 = request.form["sort_key_order2"]
            sort_key3 = request.form["sort_key3"]
            sort_key_order3 = request.form["sort_key_order3"]
            sort_key4 = request.form["sort_key4"]
            sort_key_order4 = request.form["sort_key_order4"]

            if sort_key0 is not None and len(sort_key0.strip()) > 0:
                sort_dict0 = {'property_id': int(sort_key0), 'sort_key_order': sort_key_order0}
                listFormatSortList.append(sort_dict0)

            if sort_key1 is not None and len(sort_key1.strip()) > 0:
                sort_dict1 = {'property_id': int(sort_key1), 'sort_key_order': sort_key_order1}
                listFormatSortList.append(sort_dict1)

            if sort_key2 is not None and len(sort_key2.strip()) > 0:
                sort_dict2 = {'property_id': int(sort_key2), 'sort_key_order': sort_key_order2}
                listFormatSortList.append(sort_dict2)

            if sort_key3 is not None and len(sort_key3.strip()) > 0:
                sort_dict3 = {'property_id': int(sort_key3), 'sort_key_order': sort_key_order3}
                listFormatSortList.append(sort_dict3)

            if sort_key4 is not None and len(sort_key4.strip()) > 0:
                sort_dict4 = {'property_id': int(sort_key4), 'sort_key_order': sort_key_order4}
                listFormatSortList.append(sort_dict4)

        if len(formatIdList) > 0:
            listFormatColumnsList = getSelectFormatColumns(formatIdList, object_type_id)

        # 入力チェックする
        cname = [
            'Display Order',
            'Remarks'
        ]
        input_value = [
            StrUtil.trim(form.displayOrder.data),
            StrUtil.trim(form.remarks.data)
        ]
        db_field = [
            'DISPLAY_ORDER',
            'REMARKS'
        ]
        col_prop = {'cname': cname, 'input_value': input_value, 'db_field': db_field}
        param_prop = {'err_msgs': [], 'table_name': 'CMS_LIST_FORMAT', 'form': form, 'col_prop': col_prop}
        DbUtil.check_input_form_data_by_db(param_prop)

        if len(param_prop['err_msgs']) > 0:
            err_msgs = param_prop['err_msgs']
            isSaveError = True

        if request.method == 'POST':
            editMode = request.form["editMode"]

        if request.method == 'POST' and not isSaveError:
            if form.validate_on_submit() == False:
                StrUtil.print_debug('format_edit validate error')
            else:
                try:
                    if 'New' == editMode:
                        cmsCommon = CmsCommon()
                        format_Id = cmsCommon.getObjectIdSeq()
                        form.formatId.data = format_Id
                        # 追加　CmsListFormat
                        cmsListFormat = getCmsListFormat(cmsListFormat, form)
                        CmsListFormat().addCmsListFormat(cmsListFormat)
                    elif 'Edit' == editMode:
                        # 更新 CmsListFormat
                        cmsListFormat = CmsListFormat().getCmsListFormat(form.formatId.data)
                        cmsListFormat = getCmsListFormat(cmsListFormat, form)
                        format_Id = form.formatId.data
                        # 削除 cmsListFormatColumns
                        CmsListFormatColumns().delCmsListFormatColumns(form.formatId.data)
                        if format_type == Const.LIST:
                            # 削除 CmsListFormatSort
                            CmsListFormatSort().delCmsListFormatSort(form.formatId.data)
                    # 追加 CmsListFormatColumns
                    addFormatColumns(format_Id, formatIdList, object_type_id)

                    # 追加 CmsListFormatSort
                    # cms_list_format.format_type = 'LIST'の場合
                    if format_type == Const.LIST:
                        orderNum = 1
                        if sort_key0 is not None and len(sort_key0.strip()) > 0:
                            addListFormatSort(format_Id, orderNum, sort_key0, sort_key_order0)
                            orderNum = orderNum + 1

                        if sort_key1 is not None and len(sort_key1.strip()) > 0:
                            addListFormatSort(format_Id, orderNum, sort_key1, sort_key_order1)
                            orderNum = orderNum + 1

                        if sort_key2 is not None and len(sort_key2.strip()) > 0:
                            addListFormatSort(format_Id, orderNum, sort_key2, sort_key_order2)
                            orderNum = orderNum + 1

                        if sort_key3 is not None and len(sort_key3.strip()) > 0:
                            addListFormatSort(format_Id, orderNum, sort_key3, sort_key_order3)
                            orderNum = orderNum + 1

                        if sort_key4 is not None and len(sort_key4.strip()) > 0:
                            addListFormatSort(format_Id, orderNum, sort_key4, sort_key_order4)

                    db.session.commit()
                    return redirect(url_for(redirectUrl, db_id=db_id))
                except Exception as e:
                    db.session.rollback()
                    tb = sys.exc_info()[2]
                    StrUtil.print_error('error_msg:{}'.format(str(e.with_traceback(tb))))
                    err_msgs.append('List Format save failed.')

    if editMode == 'New':
        editTitle = 'Create'
    elif editMode == 'Edit':
        editTitle = 'Modify'
    else:
        editTitle = ''

    if format_type == Const.LIST:
        formatType = 'List'
    elif format_type == Const.PROPERTY:
        formatType = 'Property'
    else:
        formatType = ''
    subTitle = editTitle + ' ' + formatType + ' ' + 'Format'
    title = 'CMS: ' + subTitle
    thTitle = formatType + ' ' + 'Format'

    # ナビゲーションリンク
    navi_arr_ref = []
    navi_arr_ref.append('Main Menu')
    navi_arr_ref.append(url_for('adm_index'))
    navi_arr_ref.append('Database')
    navi_arr_ref.append(url_for('database_admin'))
    navi_arr_ref.append(cmsDb.db_name)
    navi_arr_ref.append(url_for('database', func='database_detail', db_id=cmsDb.db_id))
    navi_arr_ref.append(thTitle)

    return render_template(
        page_id,
        title=title,
        navi_bar_html=HtmlUtil.print_navi_bar(navi_arr_ref),
        err_msgs=err_msgs,
        subTitle=subTitle,
        thTitle=thTitle,
        current_user=current_user,
        db_id=db_id,
        format_type=format_type,
        editMode=editMode,
        form=form,
        propertyNameList=propertyNameList,
        listFormatColumnsList=listFormatColumnsList,
        listFormatSortList=listFormatSortList,
        cmsDb=cmsDb,
        func=func,
        appVer=current_app.config['APP_VER'])


# Format 削除処理
def format_delete(func, db_id, format_type, format_id):
    err_msgs = []
    cmsDb = CmsDb.getCmsDbProperty(db_id)

    redirectUrl = 'list_format'
    page_id = 'cms_admin/list_format_delete.html'
    title = 'CMS：List Format'
    subTitle = 'Delete List Format'
    thTitle = 'List Format'
    if format_type == Const.PROPERTY:
        redirectUrl = 'property_format'
        page_id = 'cms_admin/property_format_delete.html'
        title = 'CMS：Property Format'
        subTitle = 'Delete Property Format'
        thTitle = 'Property Format'

    # ナビゲーションリンク
    navi_arr_ref = []
    navi_arr_ref.append('Main Menu')
    navi_arr_ref.append(url_for('adm_index'))
    navi_arr_ref.append('Database')
    navi_arr_ref.append(url_for('database_admin'))
    navi_arr_ref.append(cmsDb['db_name'])
    navi_arr_ref.append(url_for('database', func='database_detail', db_id=cmsDb['db_id']))
    navi_arr_ref.append(thTitle)
    navi_arr_ref.append(url_for(redirectUrl, db_id=cmsDb['db_id']))

    listFormat = CmsListFormat().getCmsListFormat(format_id)

    # List format  削除処理
    pkgCmsSecurity = PkgCmsSecurity()
    if func == 'list_format_delete':
        # 削除可能かチェック
        if not format_id or not pkgCmsSecurity.isListFormatDelete(format_id, current_user.get_id()):
            err_msgs.append('Can not delete this List Format.')
        else:
            try:
                CmsListFormat().delCmsListFormat(format_id)
                # 削除 cmsListFormatColumns
                CmsListFormatColumns().delCmsListFormatColumns(format_id)
                # 削除 CmsListFormatSort
                CmsListFormatSort().delCmsListFormatSort(format_id)
                db.session.commit()
                return redirect(url_for(redirectUrl, db_id=db_id))
            except Exception as e:
                db.session.rollback()
                tb = sys.exc_info()[2]
                StrUtil.print_error('error_msg:{}'.format(str(e.with_traceback(tb))))
                err_msgs.append('List Format delete failed.')

    # property format  削除処理
    elif func == 'property_format_delete':
        # 削除可能かチェック
        if not format_id or not pkgCmsSecurity.isListFormatDelete(format_id, current_user.get_id()):
            err_msgs.append('Can not delete this Property Format.')
        else:
            try:
                CmsListFormat().delCmsListFormat(format_id)
                # 削除 cmsListFormatColumns
                CmsListFormatColumns().delCmsListFormatColumns(format_id)
                db.session.commit()
                return redirect(url_for(redirectUrl, db_id=db_id))
            except Exception as e:
                db.session.rollback()
                tb = sys.exc_info()[2]
                StrUtil.print_error('error_msg:{}'.format(str(e.with_traceback(tb))))
                err_msgs.append('List Format delete failed.')

    return render_template(
        page_id,
        title=title,
        navi_bar_html=HtmlUtil.print_navi_bar(navi_arr_ref),
        subTitle=subTitle,
        err_msgs=err_msgs,
        db_id=db_id,
        format_id=format_id,
        listFormat=listFormat,
        cmsDb=cmsDb,
        current_user=current_user,
        appVer=current_app.config['APP_VER'])


def format_jqmodal(request):
    object_type_id = request.args.get("object_type_id")
    dataList = request.args.get("data_list")
    format_type = request.args.get("format_type")
    propertyList = []
    if len(dataList) > 0:
        selectFormatColumns = getSelectFormatColumns(dataList, object_type_id)
        for column in selectFormatColumns:
            propertyList.append(column.get('property_name'))
    return render_template(
        'cms_admin/format_jqmodal.html',
        propertyList=propertyList,
        jqmTitle='Preview',
        format_type=format_type
    )


def getListFormatForm(format_id):
    form = ListFormatForm()
    cmsListFormat = CmsListFormat().getCmsListFormat(format_id)
    form.formatId.data = cmsListFormat.format_id
    form.objectTypeId.data = cmsListFormat.object_type_id
    form.formatType.data = cmsListFormat.format_type
    form.displayOrder.data = cmsListFormat.display_order
    form.remarks.data = cmsListFormat.remarks
    return form


def getCmsListFormat(cmsListFormat, form):
    cmsListFormat.format_id = form.formatId.data
    cmsListFormat.object_type_id = form.objectTypeId.data
    cmsListFormat.format_type = StrUtil.trim(form.formatType.data)
    cmsListFormat.display_order = StrUtil.trim(form.displayOrder.data)
    cmsListFormat.remarks = StrUtil.trim(form.remarks.data)
    return cmsListFormat


def addFormatColumns(formatId, formatIdList, object_type_id):
    if len(formatIdList) > 0:
        index = 1
        selectFormatColumns = getSelectFormatColumns(formatIdList, object_type_id)
        for column in selectFormatColumns:
            addListFormatColumns(formatId, index, column.get('property_id'))
            index = index + 1


def addListFormatColumns(formatId, displayOrder, propertyId):
    formatColumns = CmsListFormatColumns()
    formatColumns.format_id = formatId
    formatColumns.display_order = displayOrder
    formatColumns.property_id = propertyId
    db.session.add(formatColumns)


def addListFormatSort(formatId, displayOrder, propertyId, sortKeyOrder):
    formatSort = CmsListFormatSort()
    formatSort.format_id = formatId
    formatSort.display_order = displayOrder
    formatSort.property_id = propertyId
    formatSort.sort_key_order = sortKeyOrder
    return db.session.add(formatSort)


# cms_object_propertyから選択した項目
def getSelectFormatColumns(formatIdList, object_type_id):
    objectPropertyList = []
    if len(formatIdList) > 0:
        col_list = formatIdList.split(',')
        cmsObjectProperty = CmsObjectProperty()
        for col_id in col_list:
            for ctx_obj in cmsObjectProperty.getObjectPropertyNames(object_type_id):
                property_id = str(ctx_obj.property_id)
                if col_id == property_id:
                    selection_dic = {'property_id': property_id, 'property_name': ctx_obj.property_name}
                    objectPropertyList.append(selection_dic)
    return objectPropertyList


# List/Property Format End

# Keyword management end
def keywordList(request):
    cmsKeywordSetting = CmsKeywordSetting()
    cmsKeywordMaster = CmsKeywordMaster()
    keywordList = []
    page_id = 'cms_admin/keyword_list.html'
    err_msgs = []

    db_id = request.args.get("db_id")
    cmsDb = CmsDb.getCmsDbProperty(db_id)

    # ナビゲーションリンク
    navi_arr_ref = []
    navi_arr_ref.append('Main Menu')
    navi_arr_ref.append(url_for('adm_index'))
    navi_arr_ref.append('Database')
    navi_arr_ref.append(url_for('database_admin'))
    navi_arr_ref.append(cmsDb['db_name'])
    navi_arr_ref.append(url_for('database', func='database_detail', db_id=cmsDb['db_id']))
    navi_arr_ref.append("Keyword")

    # キーワード情報を取得
    keywordSettingList = cmsKeywordSetting.getKeywordSettingList(db_id)
    for keywordSetting in keywordSettingList:
        kwSetting = CmsKeywordSetting()
        kwSetting.keyword_mst_id = keywordSetting.keyword_mst_id
        kwSetting.keyword_name = keywordSetting.keyword_name
        kwSetting.tree_separator = keywordSetting.tree_separator
        if keywordSetting.multi_set_flg == 0:
            kwSetting.multiSetFlg = '1つ設定可能'
        elif keywordSetting.multi_set_flg == 1:
            kwSetting.multiSetFlg = '複数セット可能'
        if keywordSetting.not_null_flg == 1:
            kwSetting.notNullFlg = '必須'

        # キーワード
        kList = cmsKeywordMaster.getKeywordList(keywordSetting.keyword_mst_id)
        kwSetting.setKeywords(kList)
        keywordList.append(kwSetting)

    return render_template(
        page_id,
        title='CMS：Keyword List',
        navi_bar_html=HtmlUtil.print_navi_bar(navi_arr_ref),
        err_msgs=err_msgs,
        current_user=current_user,
        cmsDb=cmsDb,
        keywordList=keywordList,
        appVer=current_app.config['APP_VER'])


# Keyword management end


# Style management start
def style_setting_list(request):
    cmsStyleMaster = CmsStyleMaster()
    page_id = 'cms_admin/style_setting_list.html'
    sub_title = 'Style Setting'
    err_msgs = []

    db_id = request.args.get("db_id")
    cmsDb = CmsDb.getCmsDbProperty(db_id)

    # ナビゲーションリンク
    navi_arr_ref = []
    navi_arr_ref.append('Main Menu')
    navi_arr_ref.append(url_for('adm_index'))
    navi_arr_ref.append('Database')
    navi_arr_ref.append(url_for('database_admin'))
    navi_arr_ref.append(cmsDb['db_name'])
    navi_arr_ref.append(url_for('database', func='database_detail', db_id=cmsDb['db_id']))
    navi_arr_ref.append(sub_title)

    # styleSetting情報を取得
    styleSettingList = cmsStyleMaster.getStyleSettingList(db_id)
    return render_template(
        page_id,
        title='CMS：Style Setting',
        navi_bar_html=HtmlUtil.print_navi_bar(navi_arr_ref),
        err_msgs=err_msgs,
        current_user=current_user,
        cmsDb=cmsDb,
        styleSettingList=styleSettingList,
        appVer=current_app.config['APP_VER'],
        const=Const)


def style_setting_edit(func, request):
    if len(func) == 0:
        return render_template('error/404.html')
    form = StyleSettingForm()
    page_id = 'cms_admin/style_setting_edit.html'
    err_msgs = []
    is_type_color = False
    isSaveError = False
    cmsStyleSetting = CmsStyleSetting()
    cmsStyleMaster = CmsStyleMaster()

    # ChromeまたはEdgeブラウザの場合、input type='color'でカラー選択できるように
    browser = HtmlUtil.get_browser(request)
    if 'edg' == browser or 'chrome' == browser:
        is_type_color = True

    # 編集
    if func == 'edit':
        db_id = request.args.get("db_id")
        style_name = request.args.get("style_name")

        # DB情報の取得
        cmsDb = CmsDb.getCmsDb(db_id)
        form.dbId.data = db_id
        form.dbName.data = cmsDb.db_name

        styleSettingInfo = cmsStyleMaster.getStyleSettingInfo(db_id, style_name)
        form.styleName.data = style_name
        form.styleType.data = styleSettingInfo.style_type
        form.value.data = str(styleSettingInfo.value or '')
        form.defaultValue.data = str(styleSettingInfo.default_value or '')
        form.remarks.data = styleSettingInfo.remarks

    # 保存処理
    elif func == 'save':
        # 入力チェックする
        cname = [
            form.dbId.label.text,
            'Style Name',
            'Value',
        ]
        input_value = [
            form.dbId.data,
            form.styleName.data,
            form.value.data,
        ]
        db_field = [
            form.dbId.label.text.upper(),
            form.styleName.label.text.upper(),
            form.value.label.text.upper(),
        ]
        col_prop = {'cname': cname, 'input_value': input_value, 'db_field': db_field}
        param_prop = {'err_msgs': [], 'table_name': 'CMS_STYLE_SETTING', 'form': form, 'col_prop': col_prop}
        DbUtil.check_input_form_data_by_db(param_prop)

        # エラー発生の場合
        if len(param_prop['err_msgs']) > 0:
            err_msgs = param_prop['err_msgs']
            isSaveError = True

        # Value 入力チェック
        styleType = form.styleType.data
        colorValue = form.value.data
        if styleType == Const.STYLE_TYPE_COLOR:
            if colorValue:
                match = re.fullmatch(r'^#([A-Fa-f0-9]{3}$)|^#([A-Fa-f0-9]{6}$)', colorValue)
                if match is None:
                    err_msgs.append('Value: invalid value.')
                    isSaveError = True

        if request.method == 'POST' and not isSaveError:
            if form.validate_on_submit() == False:
                StrUtil.print_debug('style setting validate error')
            else:
                try:
                    # CMS_STYLE_SETTINGテーブルの更新
                    CmsStyleSetting().updateStyleSetting(form.dbId.data, form.styleName.data, form.value.data)
                    db.session.commit()
                    return redirect(url_for('style_setting', db_id=form.dbId.data))
                except Exception as e:
                    db.session.rollback()
                    tb = sys.exc_info()[2]
                    StrUtil.print_error('error_msg:{}'.format(str(e.with_traceback(tb))))
                    err_msgs.append('style setting save failed.')

    title = 'CMS：Update Style Setting'
    subTitle = 'Style Setting'
    th_title = 'Update Style Setting'

    # ナビゲーションリンク
    navi_arr_ref = []
    navi_arr_ref.append('Main Menu')
    navi_arr_ref.append(url_for('adm_index'))
    navi_arr_ref.append('Database')
    navi_arr_ref.append(url_for('database_admin'))
    navi_arr_ref.append(form.dbName.data)
    navi_arr_ref.append(url_for('database', func='database_detail', db_id=form.dbId.data))
    navi_arr_ref.append(subTitle)
    navi_arr_ref.append(url_for('style_setting', db_id=form.dbId.data))

    return render_template(
        page_id,
        title=title,
        navi_bar_html=HtmlUtil.print_navi_bar(navi_arr_ref),
        is_type_color=is_type_color,
        err_msgs=err_msgs,
        thTitle=th_title,
        current_user=current_user,
        form=form,
        appVer=current_app.config['APP_VER'],
        const=Const)


# Style Setting end

# IPアドレス management start
# IPアドレスリスト管理画面へ遷移
def ip_addr_master_list():
    # ナビゲーションリンク
    navi_arr_ref = []
    navi_arr_ref.append('Main Menu')
    navi_arr_ref.append(url_for('adm_index'))
    navi_arr_ref.append('IP address List')

    ipAddrMasterList = CmsIpAddrListMaster().getCmsIpAddrListMasters()
    return render_template(
        'cms_admin/ip_addr_admin.html',
        title='CMS：IP Address Management',
        navi_bar_html=HtmlUtil.print_navi_bar(navi_arr_ref),
        ipAddrMasterList=ipAddrMasterList,
        current_user=current_user,
        appVer=current_app.config['APP_VER'])


# IPアドレスリスト画面へ遷移
def ip_addr_list(ip_addr_list_id):
    ipAddrMaster = CmsIpAddrListMaster().getCmsIpAddrListMaster(ip_addr_list_id)
    ipAddrList = CmsIpAddrList().getCmsIpAddrList(ip_addr_list_id)

    # ナビゲーションリンク
    navi_arr_ref = []
    navi_arr_ref.append('Main Menu')
    navi_arr_ref.append(url_for('adm_index'))
    navi_arr_ref.append('IP address List')
    navi_arr_ref.append(url_for('ip_addr_admin'))
    navi_arr_ref.append(ipAddrMaster.ip_addr_list_name)

    return render_template(
        'cms_admin/ip_addr_list.html',
        title='CMS：IP Address List',
        navi_bar_html=HtmlUtil.print_navi_bar(navi_arr_ref),
        ipAddrMaster=ipAddrMaster,
        ipAddrList=ipAddrList,
        current_user=current_user,
        appVer=current_app.config['APP_VER'])


# IPアドレスの保存・削除処理
def service_ip_addr(func, ip_addr_list_id, request):
    if len(func) == 0 or len(ip_addr_list_id) == 0:
        return render_template('error/404.html')

    form = IpAddrForm()
    cmsIpAddress = CmsIpAddrList()
    editMode = 'Edit'
    page_id = 'cms_admin/ip_addr_edit.html'
    err_msgs = []
    isSaveError = False
    ipAddrMaster = CmsIpAddrListMaster().getCmsIpAddrListMaster(ip_addr_list_id)

    # ナビゲーションリンク
    navi_arr_ref = []
    navi_arr_ref.append('Main Menu')
    navi_arr_ref.append(url_for('adm_index'))
    navi_arr_ref.append('IP address List')
    navi_arr_ref.append(url_for('ip_addr_admin'))
    navi_arr_ref.append(ipAddrMaster.ip_addr_list_name)
    navi_arr_ref.append(url_for('ip_addr_list', ip_addr_list_id=ipAddrMaster.ip_addr_list_id))

    # 新規・編集
    if func == 'ip_addr_edit':
        ip_address = request.args.get("ip_address")
        # 新規の場合
        if ip_address is None or len(ip_address) == 0:
            editMode = 'New'
            form.ipAddrListId.data = ip_addr_list_id
        else:
            # 編集の場合
            form = getCmsIpAddrForm(ip_addr_list_id, ip_address)
            editMode = 'Edit'
    # 保存処理
    elif func == 'ip_addr_save':
        # 入力チェックする
        cname = [
            form.ipAddress.label.text,
            form.subnetMask.label.text,
            form.remarks.label.text
        ]
        input_value = [
            StrUtil.trim(form.ipAddress.data),
            StrUtil.trim(form.subnetMask.data),
            StrUtil.trim(form.remarks.data)
        ]
        db_field = [
            form.ipAddress.label.text.upper(),
            form.subnetMask.label.text.upper(),
            form.remarks.label.text.upper()
        ]
        col_prop = {'cname': cname, 'input_value': input_value, 'db_field': db_field}
        param_prop = {'err_msgs': [], 'table_name': 'CMS_IP_ADDR_LIST', 'form': form, 'col_prop': col_prop}
        DbUtil.check_input_form_data_by_db(param_prop)

        if len(param_prop['err_msgs']) > 0:
            err_msgs = param_prop['err_msgs']
            isSaveError = True

        # IP_ADDRESSに重複チェック
        if not isSaveError:
            checkIpAddress = CmsIpAddrList().getCmsCmsIpAddress(ip_addr_list_id, StrUtil.trim(form.ipAddress.data))
            if ('New' == editMode and checkIpAddress is not None) \
                    or ('Edit' == editMode and checkIpAddress is not None
                        and checkIpAddress.ip_address != form.ipAddressOrg.data):
                err_msgs.append(Const.IP_ADDRESS_OVERLAP_ERR_MSG)
                isSaveError = True

        if request.method == 'POST':
            editMode = request.form["editMode"]

        if request.method == 'POST' and not isSaveError:
            if form.validate_on_submit() == False:
                StrUtil.print_debug('service_database validate error')
            else:
                try:
                    if 'New' == editMode:
                        cmsIpAddress = getCmsIpAddress(cmsIpAddress, form)
                        CmsIpAddrList().addCmsIpAddr(cmsIpAddress, current_user.get_id())
                        db.session.commit()
                    else:
                        cmsIpAddress = CmsIpAddrList().getCmsCmsIpAddress(form.ipAddrListId.data,
                                                                          form.ipAddressOrg.data)
                        cmsIpAddress = getCmsIpAddress(cmsIpAddress, form)
                        CmsIpAddrList().updateCmsIpAddr(cmsIpAddress, current_user.get_id())
                        db.session.commit()

                    return redirect(url_for('ip_addr_list', ip_addr_list_id=ip_addr_list_id))
                except Exception as e:
                    db.session.rollback()
                    tb = sys.exc_info()[2]
                    StrUtil.print_error('error_msg:{}'.format(str(e.with_traceback(tb))))
                    err_msgs.append(Const.IP_ADDRESS_SAVE_ERROR)
    # 削除処理
    elif func == 'ip_addr_delete':
        ip_address = request.args.get("ip_address")
        try:
            CmsIpAddrList().delCmsIpAddr(ip_addr_list_id, ip_address)
            db.session.commit()
            return redirect(url_for('ip_addr_list', ip_addr_list_id=ip_addr_list_id))
        except Exception as e:
            db.session.rollback()
            tb = sys.exc_info()[2]
            StrUtil.print_error('error_msg:{}'.format(str(e.with_traceback(tb))))
            err_msgs.append('IP Address delete failed.')

    if editMode == 'New':
        title = 'CMS：Create IP Address'
        subTitle = 'Create IP Address'
    elif editMode == 'Edit':
        title = 'CMS：Modify IP Address'
        subTitle = 'Modify IP Address'
    else:
        title = 'CMS：'
        subTitle = ''
    return render_template(
        page_id,
        title=title,
        navi_bar_html=HtmlUtil.print_navi_bar(navi_arr_ref),
        err_msgs=err_msgs,
        subTitle=subTitle,
        current_user=current_user,
        editMode=editMode,
        ipAddrMaster=ipAddrMaster,
        form=form,
        appVer=current_app.config['APP_VER'])


def getCmsIpAddrForm(ip_addr_list_id, ip_address):
    form = IpAddrForm()
    cmsIpAddress = CmsIpAddrList().getCmsCmsIpAddress(ip_addr_list_id, ip_address)
    form.ipAddrListId.data = cmsIpAddress.ip_addr_list_id
    form.ipAddress.data = cmsIpAddress.ip_address
    form.ipAddressOrg.data = cmsIpAddress.ip_address
    form.subnetMask.data = cmsIpAddress.subnet_mask
    form.remarks.data = cmsIpAddress.remarks
    return form


def getCmsIpAddress(cmsIpAddress, form):
    cmsIpAddress.ip_addr_list_id = form.ipAddrListId.data
    cmsIpAddress.ip_address = StrUtil.trim(form.ipAddress.data)
    cmsIpAddress.subnet_mask = StrUtil.trim(form.subnetMask.data)
    cmsIpAddress.remarks = form.remarks.data
    return cmsIpAddress


# IPアドレス management end

def selection_mng():
    selection_msts = CmsObjectPropSelectionMst.query.filter(
        CmsObjectPropSelectionMst.db_id == request.args.get("db_id"),
        CmsObjectPropSelectionMst.is_deleted == 0
    ).order_by(CmsObjectPropSelectionMst.display_order).all()
    # g.navi_arr_ref.append("Selection Master")
    return render_template(
        "cms_admin/selection_mng_list.html",
        title="CMS：Selection Master",
        selection_msts=selection_msts
    )
