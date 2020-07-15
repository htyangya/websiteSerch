from flask import session, request, redirect, render_template, url_for, flash, current_app
from flask_login import login_user, current_user

import app.lib.cms_lib.session
from app import db
from app.controllers.package import PkgUserAuth, PkgCmsLog, PkgCmsErrLog
from app.forms.login_form import LoginForm
from app.lib.cms_lib.session import set_cookie
from app.lib.cms_lib.str_util import StrUtil
from app.lib.conf.const import Const
from app.models.user import User


def doLogin(db_id, form):
    if len(db_id) == 0:
        flash('[db_id]パラメータを入れてください')
        return render_template('error/404.html')

    # データベースオブジェクトを取得する
    current_db = app.lib.cms_lib.session.get_current_db(db_id)

    # グローバル変数に設定する
    app.lib.cms_lib.session.current_db = current_db

    if current_db is None:
        flash('[db_id:{}]情報を取得できません'.format(db_id))
        return render_template('error/404.html')
    StrUtil.print_debug("login_required. cur_db.db_id=[{}]".format(str(current_db.db_id)))

    # リダイレクトURLを取得する
    next_url = _get_next_url()

    if form.validate_on_submit():
        user = User.query.filter_by(tuid=form.user_id.data).first()
        if user is None or not PkgUserAuth.check_passwd_for_cms(form.user_id.data, form.password.data):
            # エラーログを記録する
            pkgCmsErrLog = PkgCmsErrLog()
            pkgCmsErrLog.saveErrLog('LOGIN_ERROR', str(form.user_id.data), str(current_db.db_id), '')
            db.session.commit()
            flash('invalid user_id or password')
            return redirect(url_for('login', db_id=db_id, user_id=form.user_id.data, next_url=next_url))
        login_user(user, False)
        session['last_login_user_id'] = form.user_id.data
        session[str(db_id) + '_is_edit_mode'] = False

        # ログインログを記録する
        pkgCmsLog = PkgCmsLog()
        pkgCmsLog.saveOperationLog(form.user_id.data, db_id, operation_cd=Const.OPERATION_CD_LOGIN, object_type='DB',
                                   note=current_db.db_name)
        db.session.commit()
        return set_cookie(current_db.session_cookie_name, current_user.tuid, url_for('index', db_id=db_id))

    # ログイン情報を保持する
    last_login_user_id = StrUtil.get_safe_edit_mode('last_login_user_id', session)
    user_id = request.args.get('user_id') or last_login_user_id
    if user_id:
        form.user_id.data = user_id

    user_name = ''
    if current_user.is_active:
        user_name = current_user.get_user_name()

    return render_template(
        'login.html',
        title=current_db.db_name + '-ログイン画面',
        systemVersion="Developer Version 1.00",
        form=form,
        db_id=db_id,
        next_url=next_url,
        db_name=current_db.db_name,
        user_name=user_name,
        loginMessage=current_db.login_message,
    )


def redirectDbAdmin(db_id):
    if len(db_id) == 0:
        flash('[db_id]パラメータを入れてください')
        return render_template('error/404.html')
    # データベースオブジェクトを取得する
    current_db = app.lib.cms_lib.session.get_current_db(db_id)
    # グローバル変数に設定する
    app.lib.cms_lib.session.current_db = current_db

    if current_db is None:
        flash('[db_id:{}]情報を取得できません'.format(db_id))
        return render_template('error/404.html')
    StrUtil.print_debug("db_adm_login_required. cur_db.db_id=[{}]".format(str(current_db.db_id)))

    if current_user.is_active:
        session['last_login_user_id'] = current_user.get_id()
        return set_cookie(StrUtil.get_safe_config(current_app, 'CMS_DB_SYS_COOKIE'),
                          current_user.tuid, url_for('db_adm_index', db_id=db_id))

    form = LoginForm()
    # ログイン情報を保持する
    last_login_user_id = StrUtil.get_safe_edit_mode('last_login_user_id', session)
    user_id = request.args.get('user_id') or last_login_user_id
    if user_id:
        form.user_id.data = user_id

    return render_template(
        'cms_admin/login.html',
        form=form,
        db_id=db_id,
        db_name=current_db.db_name,
        systemVersion="Developer Version 1.00")


def doDbAdminLogin(db_id, form):
    if len(db_id) == 0:
        flash('[db_id]パラメータを入れてください')
        return render_template('error/404.html')

    # データベースオブジェクトを取得する
    current_db = app.lib.cms_lib.session.get_current_db(db_id)

    # グローバル変数に設定する
    app.lib.cms_lib.session.current_db = current_db

    if current_db is None:
        flash('[db_id:{}]情報を取得できません'.format(db_id))
        return render_template('error/404.html')
    StrUtil.print_debug("db_adm_login_required. cur_db.db_id=[{}]".format(str(current_db.db_id)))

    # リダイレクトURLを取得する
    next_url = _get_next_url()

    if form.validate_on_submit():
        user = User.query.filter_by(tuid=form.user_id.data).first()
        if user is None or not PkgUserAuth.check_passwd_for_cms(form.user_id.data, form.password.data):
            # エラーログを記録する
            pkgCmsErrLog = PkgCmsErrLog()
            pkgCmsErrLog.saveErrLog('LOGIN_ERROR', str(form.user_id.data), str(current_db.db_id), '')
            db.session.commit()
            flash('invalid user_id or password')
            return redirect(url_for('db_adm_login', db_id=db_id, user_id=form.user_id.data, next_url=next_url))
        login_user(user, False)
        session['last_login_user_id'] = form.user_id.data

        return set_cookie(StrUtil.get_safe_config(current_app, 'CMS_DB_SYS_COOKIE'),
                          current_user.tuid, url_for('db_adm_index', db_id=db_id))

    # ログイン情報を保持する
    last_login_user_id = StrUtil.get_safe_edit_mode('last_login_user_id', session)
    user_id = request.args.get('user_id') or last_login_user_id
    if user_id:
        form.user_id.data = user_id

    return render_template(
        'cms_db_admin/login.html',
        form=form,
        db_id=db_id,
        db_name=current_db.db_name,
        next_url=next_url,
        systemVersion="Developer Version 1.00")


def doAdminLogin(form):
    # リダイレクトURLを取得する
    next_url = _get_next_url()

    if form.validate_on_submit():
        user = User.query.filter_by(tuid=form.user_id.data).first()
        if user is None or not PkgUserAuth.check_passwd_for_cms(form.user_id.data, form.password.data):
            # エラーログを記録する
            pkgCmsErrLog = PkgCmsErrLog()
            pkgCmsErrLog.saveErrLog('LOGIN_ERROR', str(form.user_id.data), '', '')
            db.session.commit()
            flash('invalid user_id or password')
            return redirect(url_for('adm_login', user_id=form.user_id.data, next_url=next_url))
        login_user(user, False)
        session['last_login_user_id'] = form.user_id.data

        return set_cookie(StrUtil.get_safe_config(current_app, 'CMS_SYS_COOKIE'),
                          current_user.tuid, url_for('adm_index'))

    # ログイン情報を保持する
    last_login_user_id = StrUtil.get_safe_edit_mode('last_login_user_id', session)
    user_id = request.args.get('user_id') or last_login_user_id
    if user_id:
        form.user_id.data = user_id

    return render_template(
        'cms_admin/login.html',
        form=form,
        next_url=next_url,
        systemVersion="Developer Version 1.00")


def _get_next_url():
    # リダイレクトURLを取得する
    if request.method == 'GET':
        next_url = request.args.get('next_url')
    else:
        next_url = request.form['next_url']

    if not next_url:
        next_url = ''

    return next_url
