import re
import urllib
from functools import wraps

from flask import session, flash, url_for, request, current_app
from flask_login import login_user, logout_user
from werkzeug.utils import redirect

import flaskr.lib.svcdb_lib.session
from flaskr.controllers.package import PkgSvcdbSecurity, PkgIpAddrUtil
from flaskr.lib.conf.const import Const
from flaskr.lib.svcdb_lib.str_util import StrUtil
from flaskr.models.svcdb_session_table import SvcdbSessionTable
from flaskr.models.user import User


class UserAuth:

    def __init__(self, func):
        self._func = func

    def save_cookie(self):
        return

    def login_required(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logout_user()
            StrUtil.print_debug('login_required. func=[' + func.__name__ + ']')
            """
            db_id = flaskr.lib.svcdb_lib.session.get_db_id()
            if not db_id:
                flash('[db_id]パラメータが必要です')
                return redirect(url_for('login'))

            # データベースオブジェクトを取得する
            current_db = flaskr.lib.svcdb_lib.session.get_current_db(db_id)

            # グローバル変数に設定する
            flaskr.lib.svcdb_lib.session.current_db = current_db

            if not current_db:
                flash('[db_id:{}]情報を取得できません'.format(db_id))
                return redirect(url_for('login', db_id=db_id))
            StrUtil.print_debug('login_required. cur_db.db_id=[' + str(current_db.db_id) + ']')

            # アクセス権限チェック
            pkgIpAddrUtil = PkgIpAddrUtil()
            id_addr = StrUtil.get_ip_addr()
            if not id_addr or not pkgIpAddrUtil.isDbIpAddrVisible(db_id, id_addr):
                flash('利用権限がありません')
                return redirect(url_for('login', db_id=db_id))
            session_id = flaskr.lib.svcdb_lib.session.get_session_id(current_db.session_cookie_name)
            """
            session_id = flaskr.lib.svcdb_lib.session.get_session_id(Const.SESSION_COOKIE_NAME)
            if session_id:
                StrUtil.print_debug('login_required. session_cookie_name:{0}  session_id:{1}'.format(
                    Const.SESSION_COOKIE_NAME, session_id))

                # セッションテーブルからユーザIDを取得する（有効期限：一週間）
                cst = SvcdbSessionTable.get_session_info(Const.SESSION_COOKIE_NAME, session_id)
                if cst is None:
                    flash('invalid user_id or password')
                    return redirect(url_for('login'))

                # 取得したユーザIDでユーザ情報を取得する
                user = User.query.filter_by(tuid=cst.user_id).first()
                if user is None:
                    flash('invalid user_id or password')
                    return redirect(url_for('login'))

                """
                # 参照権限チェック
                pkgSvcdbSecurity = PkgSvcdbSecurity()
                if not pkgSvcdbSecurity.isDbVisible(db_id, user.tuid):
                    flash('このDBを参照する権限がありません')
                    return redirect(url_for('login', db_id=db_id))
                """

                StrUtil.print_debug('login_required. user_id=[' + str(cst.user_id) + ']')
                login_user(user, False)
            else:
                StrUtil.print_debug('login_required. no session id got.')
                return redirect(UserAuth._get_redirect_url(url_for('login')))

            return func(*args, **kwargs)

        return wrapper

    def adm_login_required(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logout_user()
            StrUtil.print_debug('adm_login_required. func=[' + func.__name__ + ']')

            session_id = flaskr.lib.svcdb_lib.session.get_session_id(StrUtil.get_safe_config(current_app, 'SVCDB_SYS_COOKIE'))
            if session_id:
                StrUtil.print_debug('login_required. session_cookie_name:{0}  session_id:{1}'.format(
                    'ADMIN_SESSION_COOKIE', session_id))

                cst = SvcdbSessionTable.get_adm_session_info(session_id)
                if cst is None:
                    flash('invalid user_id or password')
                    return redirect(url_for('adm_login'))

                # 取得したユーザIDでユーザ情報を取得する
                user = User.query.filter_by(tuid=cst.user_id).first()
                if user is None:
                    flash('invalid user_id or password')
                    return redirect(url_for('adm_login'))

                # 管理者権限チェック
                pkgSvcdbSecurity = PkgSvcdbSecurity()
                if not pkgSvcdbSecurity.isAdminUser(user.tuid):
                    flash('利用権限がありません')
                    return redirect(UserAuth._get_redirect_url(url_for('adm_login')))

                login_user(user, False)
            else:
                StrUtil.print_debug('login_required. no session id got.')
                return redirect(UserAuth._get_redirect_url(url_for('adm_login')))

            return func(*args, **kwargs)

        return wrapper

    def _get_redirect_url(url):
        url_opt = '?'
        if re.search('\?', url):
            url_opt = '&'

        next_url = request.url
        return '{}{}next_url={}'.format(url, url_opt, urllib.parse.quote(next_url))
