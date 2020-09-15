import sys

from flask import render_template, current_app, url_for
from flask_login import current_user
from werkzeug.utils import redirect

from app import db
from app.controllers.package import PkgCmsSecurity
from app.forms.list_format_form import ListFormatForm
from app.lib.cms_lib.db_util import DbUtil
from app.lib.cms_lib.str_util import StrUtil
from app.models.cms_common import CmsCommon
from app.models.cms_db import CmsDb
from app.models.cms_list_format import CmsListFormat
from app.models.cms_list_format_columns import CmsListFormatColumns
from app.models.cms_list_format_sort import CmsListFormatSort
from app.models.cms_object_property import CmsObjectProperty
from app.models.cms_object_type import CmsObjectType


# List Format リスト画面へ遷移
def list_format_list(request):
    db_id = request.args.get("db_id")
    format_type_flag = request.args.get("format_type_flag")
    cmsDb = CmsDb()
    cmsDb = CmsDb.getCmsDbProperty(db_id)

    format_type = 'LIST'
    page_id = 'cms_admin/list_format_list.html'
    title = 'CMS：List Format List'
    subtitle = 'List Format List'
    if format_type_flag == '1':
        format_type = 'PROPERTY'
        title = 'CMS：Property Format List'
        subtitle = 'Property Format List'
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
        subtitle=subtitle,
        objectTypeDic=objectTypeDic,
        listFormatDic=listFormatDic,
        cmsDb=cmsDb,
        format_type_flag=format_type_flag,
        current_user=current_user,
        appVer=current_app.config['APP_VER'])


# List Formatの新規,更新・削除処理
def list_format_edit(func, db_id, format_type_flag, object_type_id, format_id, request):
    if len(func) == 0:
        return render_template('error/404.html')
    form = ListFormatForm()
    form.objectTypeId.data = object_type_id
    editMode = 'Edit'
    page_id = 'cms_admin/list_format_edit.html'
    err_msgs = []
    isSaveError = False
    listFormatColumnsList = None
    listFormatSortList = None
    cmsListFormat = CmsListFormat()

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
    if func == 'list_format_edit':
        # 新規の場合
        if format_id is None or len(format_id) == 0:
            editMode = 'New'
        else:
            # 編集の場合
            form = getListFormatForm(format_id)
            listFormatColumnsList = CmsListFormatColumns().getCmsListFormatColumnsList(format_id)
            listFormatSortList = CmsListFormatSort().getCmsListFormatSortList(format_id)
            editMode = 'Edit'

    # 保存処理
    elif func == 'list_format_save':
        format_Id = ''
        propertyIdList = request.form["propertyIdList"]
        # cms_list_format.format_type = ‘LIST’の場合
        if format_type_flag == '0':
            sort_key0 = request.form["sort_key0"]
            sort_key_order0 = request.form["sort_key_order0"]
            sort_key1 = request.form["sort_key1"]
            sort_key_order1 = request.form["sort_key_order1"]
            sort_key2 = request.form["sort_key2"]
            sort_key_order2 = request.form["sort_key_order2"]
            sort_key3 = request.form["sort_key3"]
            sort_key_order3 = request.form["sort_key_order3"]

        # 入力チェックする
        cname = [
            'FORMAT TYPE',
            'DISPLAY ORDER'
        ]
        input_value = [
            StrUtil.trim(form.formatType.data),
            StrUtil.trim(form.displayOrder.data)
        ]
        db_field = [
            'FORMAT_TYPE',
            'DISPLAY_ORDER'
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
                StrUtil.print_debug('service_database validate error')
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
                        if format_type_flag == '0':
                            # 削除 CmsListFormatSort
                            CmsListFormatSort().delCmsListFormatSort(form.formatId.data)
                    # 追加 CmsListFormatColumns
                    addFormatColumns(format_Id, propertyIdList, object_type_id)

                    # 追加 CmsListFormatSort
                    # cms_list_format.format_type = ‘LIST’の場合
                    if format_type_flag == '0':
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

                    db.session.commit()
                    return redirect(url_for('list_format_list', db_id=db_id, format_type_flag=format_type_flag))
                except Exception as e:
                    db.session.rollback()
                    tb = sys.exc_info()[2]
                    StrUtil.print_error('error_msg:{}'.format(str(e.with_traceback(tb))))
                    err_msgs.append('List Format save failed.')
    # 削除処理
    elif func == 'list_format_delete':
        try:
            CmsListFormat().delCmsListFormat(format_id)
            db.session.commit()
            return redirect(url_for('list_format_list', db_id=db_id, format_type_flag=format_type_flag))
        except Exception as e:
            db.session.rollback()
            tb = sys.exc_info()[2]
            StrUtil.print_error('error_msg:{}'.format(str(e.with_traceback(tb))))
            err_msgs.append('List Format delete failed.')

    if editMode == 'New':
        editTitle = 'Create'
    elif editMode == 'Edit':
        editTitle = 'Modify'
    else:
        editTitle = ''

    if format_type_flag == '0':
        formatType = 'List'
    elif format_type_flag == '1':
        formatType = 'Property'
    else:
        formatType = ''
    subTitle = editTitle + ' ' + formatType + ' ' + 'Format'
    title = 'CMS: ' + subTitle
    thTitle = formatType + ' ' + 'Format'
    return render_template(
        page_id,
        title=title,
        err_msgs=err_msgs,
        subTitle=subTitle,
        thTitle=thTitle,
        current_user=current_user,
        db_id=db_id,
        format_type_flag=format_type_flag,
        editMode=editMode,
        form=form,
        propertyNameList=propertyNameList,
        listFormatColumnsList=listFormatColumnsList,
        listFormatSortList=listFormatSortList,
        cmsDb=cmsDb,
        func=func,
        appVer=current_app.config['APP_VER'])


def check_list_format_delete(request):
    format_id = request.args.get("format_id")
    # List Format削除可能かチェック
    pkgCmsSecurity = PkgCmsSecurity()
    if not format_id or not pkgCmsSecurity.isListFormatDelete(format_id, current_user.get_id()):
        return "error"
    else:
        return "success"


def list_format_jqmodal(request):
    db_id = request.args.get("db_id")
    object_type_id = request.args.get("object_type_id")
    dataList = request.args.get("data_list")
    propertyList = []
    if len(dataList) > 0:
        col_list = dataList.split(',')
        for col_id in col_list:
            cmsObjectProperty = CmsObjectProperty()
            for ctx_obj in cmsObjectProperty.getObjectPropertyNames(object_type_id):
                property_id = str(ctx_obj.property_id)
                if col_id == property_id:
                    propertyList.append(ctx_obj.property_name)
    return render_template(
        'cms_admin/list_format_jqmodal.html',
        propertyList=propertyList,
        jqmTitle='Preview')


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
    cmsListFormat.display_order = form.displayOrder.data
    cmsListFormat.remarks = StrUtil.trim(form.remarks.data)
    return cmsListFormat


def addFormatColumns(formatId, propertyList, object_type_id):
    if len(propertyList) > 0:
        index = 1
        col_list = propertyList.split(',')
        cmsObjectProperty = CmsObjectProperty()
        for ctx_obj in cmsObjectProperty.getObjectPropertyNames(object_type_id):
            property_id = str(ctx_obj.property_id)
            for col_id in col_list:
                if col_id == property_id:
                    addListFormatColumns(formatId, index, property_id)
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

#  end
