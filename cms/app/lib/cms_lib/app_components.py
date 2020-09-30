from flask import request, url_for, g
from flask_login import current_user

from app.lib.cms_lib.html_util import HtmlUtil
from app.lib.conf.config import Config
from app.lib.conf.const import Const
from app.models.cms_db_admin.cms_db import CmsDb


def args_get():
    db_id = request.args.get("db_id") or request.form.get("db_id")
    g.db_id = db_id
    if db_id and "selectionMng" in request.path:
        db_obj = CmsDb.query.filter(CmsDb.db_id == db_id, CmsDb.is_deleted == 0).first()
        g.db_name = db_obj.db_name
        g.navi_arr_ref = [
            'Main Menu', url_for('adm_index'),
            'Database', url_for('database_admin'),
            g.db_name, url_for('database', db_id=db_id, func='database_detail'),
        ]


def args_add():
    args = {
        "db_id": g.db_id,
        "current_user": current_user,
        "appVer": Config.APP_VER,
        "const": Const,
    }
    if hasattr(g, "db_name") and g.db_name:
        args["db_name"] = g.db_name
    if hasattr(g, "navi_arr_ref") and g.navi_arr_ref:
        args["navi_bar_html"] = HtmlUtil.print_navi_bar(g.navi_arr_ref)
    return args
