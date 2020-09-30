from datetime import datetime

from flask import Blueprint, render_template, request, abort, g, url_for
from flask_login import current_user
from werkzeug.utils import redirect

from app import db
from app.lib.cms_lib.db_util import DbUtil
from app.lib.cms_lib.html_util import HtmlUtil
from app.lib.cms_lib.session import get_request_data
from app.lib.cms_lib.user_auth import UserAuth
from app.lib.conf.config import Config
from app.lib.conf.const import Const
from app.models.cms_db_admin.cms_db import CmsDb
from app.models.cms_db_admin.cms_object_prop_selection_list import CmsObjectPropSelectionList
from app.models.cms_db_admin.cms_object_prop_selection_mst import CmsObjectPropSelectionMst

selectionMng = Blueprint("selectionMng", __name__, url_prefix="/cmsadmin/selectionMng")


@selectionMng.before_request
def args_check():
    db_id = request.args.get("db_id") or request.form.get("db_id")
    db_obj = CmsDb.query.filter(CmsDb.db_id == db_id, CmsDb.is_deleted == 0).first()
    if db_obj is None:
        abort(404)
    g.db_name = db_obj.db_name
    g.db_id = db_id
    g.navi_arr_ref = [
        'Main Menu', url_for('adm_index'),
        'Database', url_for('database_admin'),
        g.db_name, url_for('database', db_id=db_id, func='database_detail'),
    ]


@selectionMng.context_processor
def context_processor():
    return {
        "db_id": g.db_id,
        "db_name": g.db_name if "db_name" in g else "",
        "current_user": current_user,
        "appVer": Config.APP_VER,
        "const": Const,
        "navi_bar_html": HtmlUtil.print_navi_bar(g.navi_arr_ref),
    }


# views

@UserAuth.login_required
@selectionMng.route("/")
def index():
    selection_msts = CmsObjectPropSelectionMst.query.filter(
        CmsObjectPropSelectionMst.db_id == request.args.get("db_id"),
        CmsObjectPropSelectionMst.is_deleted == 0
    ).order_by(CmsObjectPropSelectionMst.display_order).all()
    g.navi_arr_ref.append("Selection Master")
    return render_template(
        "cms_admin/selection_mng_list.html",
        title="CMS：Selection Master",
        selection_msts=selection_msts
    )


@UserAuth.login_required
@selectionMng.route("/add", methods=['GET', 'POST'])
def add():
    checked_db_fields = ["selection_mst_name", "display_order", "remarks"]
    name_dict = {"selection_mst_name": "Name", "display_order": "Display Order", "remarks": "Remarks"}
    if DbUtil.check_fields_from_form_on_post("CMS_OBJECT_PROP_SELECTION_MST", checked_db_fields, name_dict):
        selection_mst = CmsObjectPropSelectionMst(
            selection_mst_id=request.form.get("selection_mst_id"),
            db_id=request.form.get("db_id"),
            selection_mst_name=request.form.get("selection_mst_name"),
            display_order=request.form.get("display_order"),
            remarks=request.form.get("remarks"),
        )
        db.session.add(selection_mst)
        db.session.commit()
        return redirect(url_for('selectionMng.index', db_id=request.form.get("db_id")))
    parent_url = url_for('selectionMng.index', db_id=g.db_id)
    g.navi_arr_ref.extend([
        "Selection Master", parent_url,
    ])
    return render_template(
        "cms_admin/selection_mng_modify.html",
        title="CMS：Selection Master Add",
        parent_url=parent_url,
        selection_mst=request.form,
        ope_msg="Create Selection Mst"
    )


@UserAuth.login_required
@selectionMng.route("/update", methods=['GET', 'POST'])
def update():
    mst_id = get_request_data("mst_id")
    selection_mst = CmsObjectPropSelectionMst.query.filter(CmsObjectPropSelectionMst.selection_mst_id == mst_id,
                                                           CmsObjectPropSelectionMst.is_deleted == 0).first()
    if selection_mst is None:
        abort(404)
    checked_db_fields = ["selection_mst_name", "display_order", "remarks"]
    name_dict = {"selection_mst_name": "Name", "display_order": "Display Order", "remarks": "Remarks"}
    if DbUtil.check_fields_from_form_on_post("CMS_OBJECT_PROP_SELECTION_MST", checked_db_fields, name_dict):
        selection_mst.selection_mst_name = request.form.get("selection_mst_name")
        selection_mst.display_order = request.form.get("display_order")
        selection_mst.remarks = request.form.get("remarks")
        selection_mst.updated_at = datetime.now()
        selection_mst.updated_by = current_user.get_id()
        db.session.add(selection_mst)
        db.session.commit()
        return redirect(url_for('selectionMng.detail', db_id=request.form.get("db_id"),
                                mst_id=mst_id))
    parent_url = url_for('selectionMng.detail', mst_id=mst_id, db_id=g.db_id)
    g.navi_arr_ref.extend([
        "Selection Master", url_for('selectionMng.index', db_id=g.db_id),
        selection_mst.selection_mst_name, parent_url,
    ])
    return render_template(
        "cms_admin/selection_mng_modify.html",
        title="CMS：Selection Master Modify",
        selection_mst=selection_mst if request.method == "GET" else request.form,
        parent_url=parent_url,
        ope_msg="Modify Selection Master"
    )


@UserAuth.login_required
@selectionMng.route("/delete", methods=['GET', 'POST'])
def delete():
    mst_id = get_request_data("mst_id")
    selection_mst = CmsObjectPropSelectionMst.query.get_or_404(mst_id)
    if request.method == "POST" and selection_mst.can_delete:
        selection_mst.is_deleted = 1
        selection_mst.deleted_at = datetime.now()
        selection_mst.deleted_by = current_user.get_id()
        db.session.add(selection_mst)
        db.session.commit()
        return redirect(url_for('selectionMng.index', db_id=get_request_data("db_id")))
    parent_url = url_for('selectionMng.detail', mst_id=mst_id, db_id=g.db_id)
    g.navi_arr_ref.extend([
        "Selection Master", url_for('selectionMng.index', db_id=g.db_id),
        selection_mst.selection_mst_name, parent_url,
    ])
    return render_template(
        "cms_admin/selection_mng_delete.html",
        title="CMS：Delete Selection Master",
        ope_msg="Delete Selection Master",
        delete_obj=selection_mst,
        disp_field="remarks",
        delete_msg=Const.SELECTION_MST_DELETE_MSG if selection_mst.can_delete else Const.SELECTION_MST_CAN_NOT_DELETE_MSG,
        mst_id=mst_id,
        parent_url=parent_url
    )


@UserAuth.login_required
@selectionMng.route("/detail")
def detail():
    mst_id = get_request_data("mst_id")
    selection_mst = CmsObjectPropSelectionMst.query.filter(CmsObjectPropSelectionMst.selection_mst_id == mst_id,
                                                           CmsObjectPropSelectionMst.is_deleted == 0).first()
    if selection_mst is None:
        abort(404)
    selection_list = CmsObjectPropSelectionList.query.filter(CmsObjectPropSelectionList.selection_mst_id == mst_id,
                                                             CmsObjectPropSelectionList.is_deleted == 0).order_by(
        CmsObjectPropSelectionList.display_order).all()
    g.navi_arr_ref.extend([
        "Selection Master", url_for('selectionMng.index', db_id=g.db_id),
    ])
    return render_template(
        "cms_admin/selection_mng_detail.html",
        title="CMS：Selection Master Detail",
        selection_mst=selection_mst,
        selection_list=selection_list
    )


@UserAuth.login_required
@selectionMng.route("/list_add", methods=['GET', 'POST'])
def list_add():
    mst_id = get_request_data("mst_id")
    checked_db_fields = ["selection_name", "display_order", "description"]
    name_dict = {"selection_name": "Name", "display_order": "Display Order", "description": "Description"}
    if DbUtil.check_fields_from_form_on_post("CMS_OBJECT_PROP_SELECTION_LIST", checked_db_fields, name_dict):
        selection_list = CmsObjectPropSelectionList(
            selection_mst_id=mst_id,
            selection_name=request.form.get("selection_name"),
            display_order=request.form.get("display_order"),
            description=request.form.get("description"),
        )
        db.session.add(selection_list)
        db.session.commit()
        return redirect(url_for('selectionMng.detail', db_id=request.form.get("db_id"),
                                mst_id=mst_id))
    parent_url = url_for('selectionMng.detail', mst_id=mst_id, db_id=g.db_id)
    selection_mst = CmsObjectPropSelectionMst.query.get_or_404(mst_id)
    g.navi_arr_ref.extend([
        "Selection Master", url_for('selectionMng.index', db_id=g.db_id),
        selection_mst.selection_mst_name, parent_url,
    ])
    return render_template(
        "cms_admin/selection_list_modify.html",
        title="CMS：Selection Data Create",
        selection_list=request.form,
        parent_url=parent_url,
        ope_msg="Create Selection Data"
    )


@UserAuth.login_required
@selectionMng.route("/list_update", methods=['GET', 'POST'])
def list_update():
    mst_id = get_request_data("mst_id")
    list_id = get_request_data("list_id")
    selection_list = CmsObjectPropSelectionList.query.get_or_404(list_id)
    checked_db_fields = ["selection_name", "display_order", "description"]
    name_dict = {"selection_name": "Name", "display_order": "Display Order", "description": "Description"}
    if DbUtil.check_fields_from_form_on_post("CMS_OBJECT_PROP_SELECTION_LIST", checked_db_fields, name_dict):
        selection_list.selection_name = request.form.get("selection_name") or ''
        selection_list.display_order = request.form.get("display_order")
        selection_list.description = request.form.get("description")
        selection_list.updated_at = datetime.now()
        selection_list.updated_by = current_user.get_id()
        db.session.add(selection_list)
        db.session.commit()
        return redirect(url_for('selectionMng.detail', db_id=request.form.get("db_id"),
                                mst_id=mst_id))
    parent_url = url_for('selectionMng.detail', mst_id=mst_id, db_id=g.db_id)
    selection_mst = CmsObjectPropSelectionMst.query.get_or_404(mst_id)
    g.navi_arr_ref.extend([
        "Selection Master", url_for('selectionMng.index', db_id=g.db_id),
        selection_mst.selection_mst_name, parent_url,
    ])
    return render_template(
        "cms_admin/selection_list_modify.html",
        title="CMS：Selection Data Modify",
        selection_list=selection_list if request.method == "GET" else request.form,
        parent_url=parent_url,
        ope_msg="Modify Selection Data"
    )


@UserAuth.login_required
@selectionMng.route("/list_delete", methods=['GET', 'POST'])
def list_delete():
    mst_id = get_request_data("mst_id")
    list_id = get_request_data("list_id")
    selection_list = CmsObjectPropSelectionList.query.get_or_404(list_id)
    if request.method == "POST" and selection_list.can_delete:
        selection_list.is_deleted = 1
        selection_list.deleted_at = datetime.now()
        selection_list.deleted_by = current_user.get_id()
        db.session.add(selection_list)
        db.session.commit()
        return redirect(url_for('selectionMng.detail', db_id=get_request_data("db_id"), mst_id=mst_id))
    parent_url = url_for('selectionMng.detail', mst_id=mst_id, db_id=g.db_id)
    selection_mst = CmsObjectPropSelectionMst.query.get_or_404(mst_id)
    g.navi_arr_ref.extend([
        "Selection Master", url_for('selectionMng.index', db_id=g.db_id),
        selection_mst.selection_mst_name, parent_url,
    ])
    return render_template(
        "cms_admin/selection_mng_delete.html",
        title="CMS：Delete Selection Data",
        ope_msg="Delete Selection Data",
        delete_obj=selection_list,
        disp_field="description",
        delete_msg=Const.SELECTION_DATA_DELETE_MSG if selection_list.can_delete else Const.SELECTION_DATA_CAN_NOT_DELETE_MSG,
        mst_id=mst_id,
        list_id=list_id,
        parent_url=parent_url
    )
