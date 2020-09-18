from datetime import datetime

from flask import Blueprint, render_template, jsonify, request, abort, g, url_for
from flask_login import current_user
from werkzeug.utils import redirect

from app import db
from app.controllers import route
from app.lib.cms_lib.user_auth import UserAuth
from app.lib.conf.config import Config
from app.lib.conf.const import Const
from app.models.cms_db import CmsDb
from app.models.cms_object_prop_selection_list import CmsObjectPropSelectionList
from app.models.cms_object_prop_selection_mst import CmsObjectPropSelectionMst
from app.services import selection_mng_service

selectionMng = Blueprint("selectionMng", __name__, url_prefix="/cmsadmin/selectionMng")


@selectionMng.before_request
def args_check():
    db_id = request.args.get("db_id") or request.form.get("db_id")
    db_obj = CmsDb.query.filter(CmsDb.db_id == db_id, CmsDb.is_deleted == 0).first()
    if db_obj is None:
        abort(404)
    g.db_name = db_obj.db_name
    g.db_id = db_id


@selectionMng.context_processor
def context_processor():
    return {
        "db_id": request.args.get("db_id"),
        "db_name": g.db_name if "db_name" in g else "",
        "current_user": current_user,
        "appVer": Config.APP_VER,
        "const": Const,
    }


# views

@UserAuth.login_required
@selectionMng.route("/")
def index():
    selection_msts = CmsObjectPropSelectionMst.query.filter(
        CmsObjectPropSelectionMst.db_id == request.args.get("db_id"),
        CmsObjectPropSelectionMst.is_deleted == 0
    ).order_by(CmsObjectPropSelectionMst.display_order).all()
    return render_template(
        "cms_admin/selection_mng_list.html",
        title="CMS：Selection Master",
        selection_msts=selection_msts
    )


@UserAuth.login_required
@selectionMng.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == "POST":
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
    return render_template(
        "cms_admin/selection_mng_modify.html",
        title="CMS：Selection Master Add",
    )


@UserAuth.login_required
@selectionMng.route("/<int:mst_id>/update", methods=['GET', 'POST'])
def update(mst_id):
    selection_mst = CmsObjectPropSelectionMst.query.filter(CmsObjectPropSelectionMst.selection_mst_id == mst_id,
                                                           CmsObjectPropSelectionMst.is_deleted == 0).first()
    if request.method == "POST":
        selection_mst.selection_mst_name = request.form.get("selection_mst_name")
        selection_mst.display_order = request.form.get("display_order")
        selection_mst.remarks = request.form.get("remarks")
        selection_mst.updated_at = datetime.now()
        selection_mst.updated_by = current_user.get_id()
        db.session.add(selection_mst)
        db.session.commit()
        return redirect(url_for('selectionMng.detail', db_id=request.form.get("db_id"),
                                mst_id=mst_id))

    return render_template(
        "cms_admin/selection_mng_modify.html",
        title="CMS：Selection Master Modify",
        selection_mst=selection_mst
    )


@UserAuth.login_required
@selectionMng.route("/<int:mst_id>/detail")
def detail(mst_id):
    selection_mst = CmsObjectPropSelectionMst.query.filter(CmsObjectPropSelectionMst.selection_mst_id == mst_id,
                                                           CmsObjectPropSelectionMst.is_deleted == 0).first()
    selection_list = CmsObjectPropSelectionList.query.filter(CmsObjectPropSelectionList.selection_mst_id == mst_id,
                                                             CmsObjectPropSelectionList.is_deleted == 0).all()
    return render_template(
        "cms_admin/selection_mng_detail.html",
        title="CMS：Selection Master Detail",
        selection_mst=selection_mst,
        selection_list=selection_list
    )
