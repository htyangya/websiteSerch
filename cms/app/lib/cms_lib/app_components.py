from flask import request, url_for, g
from flask_login import current_user
from app.lib.cms_lib.session import get_request_data
from app.lib.cms_lib.html_util import HtmlUtil
from app.lib.conf.config import Config
from app.lib.conf.const import Const
from app.models.cms_db_admin.cms_db import CmsDb


def add_arg_before_view():
    if "selection_mng" in request.path:
        g.db_id = get_request_data("db_id")
        g.db_name = CmsDb.query.filter(CmsDb.db_id == g.db_id, CmsDb.is_deleted == 0).first_or_404().db_name
        g.navi_arr_ref = [
            'Main Menu', url_for('adm_index'),
            'Database', url_for('database_admin'),
            g.db_name, url_for('database', db_id=get_request_data("db_id"), func='database_detail'),
        ]


def add_arg_to_template():
    args = {
        "current_user": current_user,
        "appVer": Config.APP_VER,
        "const": Const,
    }
    args.update({name: getattr(g, name) for name in g})
    if hasattr(g, "navi_arr_ref"):
        args["navi_bar_html"] = HtmlUtil.print_navi_bar(g.navi_arr_ref)

    return args
