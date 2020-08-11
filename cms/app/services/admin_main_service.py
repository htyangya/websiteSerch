import sys

from flask import render_template, current_app, url_for
from flask_login import current_user
from werkzeug.utils import redirect

from app import db
from app.forms.database_form import DatabaseForm, KeywordForm
from app.lib.cms_lib.db_util import DbUtil
from app.lib.cms_lib.str_util import StrUtil
from app.lib.conf.const import Const
from app.models.cms_common import CmsCommon
from app.models.cms_db import CmsDb
from app.models.cms_keyword_master import CmsKeywordMaster
from app.models.cms_keyword_setting import CmsKeywordSetting


def admin_main_init():
    return render_template(
        'cms_admin/main.html',
        title='ログインメイン',
        current_user=current_user,
        appVer=current_app.config['APP_VER'])


# Database management start
# データベースメニューへ遷移
def database_list():
    dbList = CmsDb().getCmsDbList()
    return render_template(
        'cms_admin/database_admin.html',
        title='CMS：Database Management',
        dbList=dbList,
        current_user=current_user,
        appVer=current_app.config['APP_VER'])


def service_database(func, request):
    if len(func) == 0:
        return render_template('error/404.html')

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
            editMode = 'Edit'
    # 保存処理
    elif func == 'database_save':

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
    return render_template(
        page_id,
        title=title,
        err_msgs=err_msgs,
        subTitle=subTitle,
        current_user=current_user,
        editMode=editMode,
        form=form,
        cmsDb=cmsDb,
        keywordList=keywordList,
        appVer=current_app.config['APP_VER'])


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
                    #return redirect(url_for('database', func='database_detail', db_id=form.dbId.data))
                    return redirect(url_for('keyword_list', db_id=form.dbId.data))
                except Exception as e:
                    db.session.rollback()
                    tb = sys.exc_info()[2]
                    StrUtil.print_error('service_keyword error_msg:{}'.format(str(e.with_traceback(tb))))
                    err_msgs.append('Keyword save failed.')

    title = 'CMS：Update Keyword'
    subTitle = 'Update Keyword'
    return render_template(
        page_id,
        title=title,
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


def keywordList(request):
    cmsDb = CmsDb()
    cmsKeywordSetting = CmsKeywordSetting()
    cmsKeywordMaster = CmsKeywordMaster()
    keywordList = []
    page_id = 'cms_admin/keyword_list.html'
    err_msgs = []

    db_id = request.args.get("db_id")
    cmsDb = CmsDb.getCmsDbProperty(db_id)
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
        err_msgs=err_msgs,
        current_user=current_user,
        cmsDb=cmsDb,
        keywordList=keywordList,
        appVer=current_app.config['APP_VER'])




# Database management end
