import re
import urllib
from functools import wraps

from flask import session, flash, url_for, request, current_app
from flask_login import login_user, logout_user
from werkzeug.utils import redirect

import app.lib.cms_lib.session
from app import db
from app.controllers.package import PkgCmsSecurity, PkgIpAddrUtil, PkgCmsErrLog
from app.lib.cms_lib.str_util import StrUtil
from app.lib.conf.const import Const
from app.models.cms_session_table import CmsSessionTable
from app.models.user import User


class UserAuth:

    def __init__(self, func):
        self._func = func

    def save_cookie(self):
        return

    def login_required(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logout_user()
            StrUtil.print_debug('login_required. func=[{}]'.format(str(func.__name__)))
            db_id = app.lib.cms_lib.session.get_db_id()
            if not db_id:
                flash('[db_id]パラメータが必要です')
                return redirect(url_for('login'))

            # データベースオブジェクトを取得する
            current_db = app.lib.cms_lib.session.get_current_db(db_id)

            # グローバル変数に設定する
            app.lib.cms_lib.session.current_db = current_db

            if not current_db:
                flash('[db_id:{}]情報を取得できません'.format(db_id))
                return redirect(url_for('login', db_id=db_id))
            StrUtil.print_debug('login_required. cur_db.db_id=[{}]'.format(str(current_db.db_id)))

            session_id = app.lib.cms_lib.session.get_session_id(current_db.session_cookie_name)
            if session_id:
                StrUtil.print_debug('login_required. session_cookie_name:{0}  session_id:{1}'.format(
                    current_db.session_cookie_name, session_id))

                # セッションテーブルからユーザIDを取得する（有効期限：一週間）
                cst = CmsSessionTable.get_session_info(current_db.session_cookie_name, session_id)
                if cst is None:
                    flash('invalid user_id or password')
                    return redirect(url_for('login', db_id=db_id))

                # 取得したユーザIDでユーザ情報を取得する
                user = User.query.filter_by(tuid=cst.user_id).first()
                if user is None:
                    flash('invalid user_id or password')
                    return redirect(url_for('login', db_id=db_id))

                # アクセス権限チェック
                pkgIpAddrUtil = PkgIpAddrUtil()
                id_addr = StrUtil.get_ip_addr()
                if not id_addr or not pkgIpAddrUtil.isDbIpAddrVisible(db_id, id_addr):
                    # ログ出力 DBの参照権限なし
                    PkgCmsErrLog().saveErrLog(Const.IP_ADDRESS_ERROR, user.tuid, str(current_db.db_id))
                    db.session.commit()
                    flash('利用権限がありません')
                    return redirect(url_for('login', db_id=db_id))

                # 参照権限チェック
                pkgCmsSecurity = PkgCmsSecurity()
                if not pkgCmsSecurity.isDbVisible(db_id, user.tuid):
                    # ログ出力 DBの参照権限なし
                    PkgCmsErrLog().saveErrLog(Const.DB_PRIVS_ERROR, user.tuid, str(current_db.db_id))
                    db.session.commit()
                    flash('このDBを参照する権限がありません')
                    return redirect(url_for('login', db_id=db_id))

                StrUtil.print_debug('login_required. user_id=[{}]'.format(str(current_db.db_id)))
                login_user(user, False)
                session['db_id'] = db_id
            else:
                StrUtil.print_debug('login_required. no session id got.')
                return redirect(UserAuth._get_redirect_url(url_for('login', db_id=current_db.db_id)))

            return func(*args, **kwargs)

        return wrapper

    def adm_login_required(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logout_user()
            StrUtil.print_debug('adm_login_required. func=[{}]'.format(str(func.__name__)))

            session_id = app.lib.cms_lib.session.get_session_id(StrUtil.get_safe_config(current_app, 'CMS_SYS_COOKIE'))
            if session_id:
                StrUtil.print_debug('login_required. session_cookie_name:{0}  session_id:{1}'.format(
                    'ADMIN_SESSION_COOKIE', session_id))

                cst = CmsSessionTable.get_adm_session_info(session_id)
                if cst is None:
                    flash('invalid user_id or password')
                    return redirect(url_for('adm_login'))

                # 取得したユーザIDでユーザ情報を取得する
                user = User.query.filter_by(tuid=cst.user_id).first()
                if user is None:
                    flash('invalid user_id or password')
                    return redirect(url_for('adm_login'))

                # 管理者権限チェック
                pkgCmsSecurity = PkgCmsSecurity()
                if not pkgCmsSecurity.isAdminUser(user.tuid):
                    flash('利用権限がありません')
                    return redirect(UserAuth._get_redirect_url(url_for('adm_login')))

                login_user(user, False)
            else:
                StrUtil.print_debug('login_required. no session id got.')
                return redirect(UserAuth._get_redirect_url(url_for('adm_login')))

            return func(*args, **kwargs)

        return wrapper

    def db_adm_login_required(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logout_user()
            StrUtil.print_debug('db_adm_login_required. func=[{}]'.format(func.__name__))
            db_id = app.lib.cms_lib.session.get_db_id()
            if not db_id:
                flash('[db_id]パラメータが必要です')
                return redirect(url_for('login'))

            # データベースオブジェクトを取得する
            current_db = app.lib.cms_lib.session.get_current_db(db_id)
            # グローバル変数に設定する
            app.lib.cms_lib.session.current_db = current_db
            # db情報チェック
            if not current_db:
                flash('[db_id:{}]情報を取得できません'.format(db_id))
                return redirect(url_for('db_adm_login', db_id=db_id))
            StrUtil.print_debug('db_adm_login_required. cur_db.db_id=[{}]'.format(str(current_db.db_id)))

            session_id = app.lib.cms_lib.session.get_session_id(
                StrUtil.get_safe_config(current_app, 'CMS_DB_SYS_COOKIE'))
            if session_id:
                StrUtil.print_debug('db_adm_login_required. session_cookie_name:{0} session_id:{1}'.format(
                    'DB_ADMIN_SESSION_COOKIE', session_id))

                cst = CmsSessionTable.get_db_adm_session_info(session_id)
                if cst is None:
                    flash('invalid user_id or password')
                    return redirect(url_for('db_adm_login'))

                # 取得したユーザIDでユーザ情報を取得する
                user = User.query.filter_by(tuid=cst.user_id).first()
                if user is None:
                    flash('invalid user_id or password')
                    return redirect(url_for('db_adm_login'))

                # DB管理者権限チェック
                pkgCmsSecurity = PkgCmsSecurity()
                if not pkgCmsSecurity.isDbAdminUser(db_id, user.tuid):
                    flash('利用権限がありません')
                    return redirect(UserAuth._get_redirect_url(url_for('db_adm_login', db_id=current_db.db_id)))

                login_user(user, False)
            else:
                StrUtil.print_debug('login_required. no session id got.')
                return redirect(UserAuth._get_redirect_url(url_for('db_adm_login', db_id=current_db.db_id)))

            return func(*args, **kwargs)

        return wrapper

    def _get_redirect_url(url):
        url_opt = '?'
        if re.search('\?', url):
            url_opt = '&'

        next_url = request.url
        return '{}{}next_url={}'.format(url, url_opt, urllib.parse.quote(next_url))
