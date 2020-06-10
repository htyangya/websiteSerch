from datetime import datetime, timedelta

from flask import current_app

from flaskr import db
from flaskr.lib.svcdb_lib.str_util import StrUtil


class SvcdbSessionTable(db.Model):
    __tablename__ = 'SVCDB_SESSION_TABLE'
    cookie_name = db.Column(db.String(100), primary_key=True)
    session_id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(db.String(20))
    login_date = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, cookie_name=None, session_id=None, user_id=None):
        self.cookie_name = cookie_name
        self.session_id = session_id
        self.user_id = user_id
        self.login_date = datetime.now()

    def get_session_info(cookie_name, session_id):
        current_time = datetime.now()

        return SvcdbSessionTable.query.filter_by(cookie_name=cookie_name, session_id=session_id) \
            .filter(SvcdbSessionTable.login_date >= current_time - timedelta(days=7)) \
            .filter(SvcdbSessionTable.login_date <= current_time).first()

    def get_adm_session_info(session_id):
        current_time = datetime.now()

        return SvcdbSessionTable.query.filter_by(cookie_name=StrUtil.get_safe_config(current_app, 'SVCDB_SYS_COOKIE'),
                                               session_id=session_id) \
            .filter(SvcdbSessionTable.login_date >= current_time - timedelta(days=7)) \
            .filter(SvcdbSessionTable.login_date <= current_time).first()
