import sys

from flask import render_template, current_app, url_for
from flask_login import current_user
from werkzeug.utils import redirect

from app import db
from app.lib.conf.const import Const
from app.lib.cms_lib.db_util import DbUtil
from app.lib.cms_lib.str_util import StrUtil
from app.forms.ip_addr_form import IpAddrForm
from app.models.cms_ip_addr_list import CmsIpAddrList
from app.models.cms_ip_addr_list_master import CmsIpAddrListMaster


# IPアドレス management start
# IPアドレスリスト管理画面へ遷移
def ip_addr_master_list():
    ipAddrMasterList = CmsIpAddrListMaster().getCmsIpAddrListMasters()
    return render_template(
        'cms_admin/ip_addr_admin.html',
        title='CMS：IP Address Management',
        ipAddrMasterList=ipAddrMasterList,
        current_user=current_user,
        appVer=current_app.config['APP_VER'])


# IPアドレスリスト画面へ遷移
def ip_addr_list(ip_addr_list_id):
    ipAddrMaster = CmsIpAddrListMaster().getCmsIpAddrListMaster(ip_addr_list_id)
    ipAddrList = CmsIpAddrList().getCmsIpAddrList(ip_addr_list_id)
    return render_template(
        'cms_admin/ip_addr_list.html',
        title='CMS：IP Address List',
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
            if ('New' == editMode and checkIpAddress is not None)\
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
                        cmsIpAddress = CmsIpAddrList().getCmsCmsIpAddress(form.ipAddrListId.data, form.ipAddressOrg.data)
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
