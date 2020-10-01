from flask import session, request, redirect, render_template, url_for, flash, current_app
from flask_login import login_user, current_user
from markupsafe import Markup

from flaskr.controllers.package import PkgUserAuth, PkgSvcdbLog
from flaskr.lib.conf.const import Const
from flaskr.lib.svcdb_lib.session import set_cookie
from flaskr.lib.svcdb_lib.str_util import StrUtil
from flaskr.models.svcdb_system_message import SvcdbSystemMessage
from flaskr.models.user import User


def doLogin(form):
    """
    if len(db_id) == 0:
        flash('[db_id]パラメータを入れてください')
        return render_template('error/404.html')

    # データベースオブジェクトを取得する
    current_db = flaskr.lib.svcdb_lib.session.get_current_db(db_id)

    # グローバル変数に設定する
    flaskr.lib.svcdb_lib.session.current_db = current_db

    if current_db is None:
        flash('[db_id:{}]情報を取得できません'.format(db_id))
        return render_template('error/404.html')
    print('login_required. cur_db.db_id=[' + str(current_db.db_id) + ']')
    """

    # リダイレクトURLを取得する
    next_url = _get_next_url()

    if form.validate_on_submit():
        user = User.query.filter_by(tuid=form.user_id.data).first()
        if user is None or not PkgUserAuth.check_passwd_for_svcdb(form.user_id.data, form.password.data):
            flash('invalid user_id or password')
            return redirect(url_for('login', user_id=form.user_id.data, next_url=next_url))
        login_user(user, False)
        session['last_login_user_id'] = form.user_id.data
        # session[str(db_id) + '_is_edit_mode'] = False

        # ログインログを記録する
        pkgSvcdbLog = PkgSvcdbLog()
        pkgSvcdbLog.saveOperationLog(form.user_id.data, '', operation_cd=Const.OPERATION_CD_LOGIN, object_type='DB',
                                     note=Const.SESSION_COOKIE_NAME)

        return set_cookie(Const.SESSION_COOKIE_NAME, current_user.tuid, 'main')

    # ログイン情報を保持する
    last_login_user_id = StrUtil.get_safe_edit_mode('last_login_user_id', session)
    user_id = request.args.get('user_id') or last_login_user_id
    if user_id:
        form.user_id.data = user_id

    user_name = ''
    if current_user.is_active:
        user_name = current_user.get_user_name()

    # システムメッセージ
    loginSystemMessage = ''
    systemMessage = SvcdbSystemMessage.getSystemMessage('LOGIN')
    if systemMessage is not None:
        loginSystemMessage = systemMessage.memo_txt
        if systemMessage.memo_format and systemMessage.memo_format == Const.HTML_FORMAT:
            loginSystemMessage = Markup(loginSystemMessage.replace('\n', '<br>'))

    return render_template(
        'login.html',
        title=Const.SYSTEM_NAME + '-ログイン画面',
        systemVersion="Developer Version 1.00",
        form=form,
        next_url=next_url,
        system_name=Const.SYSTEM_NAME,
        user_name=user_name,
        loginSystemMessage=loginSystemMessage,
    )


def doAdminLogin(form):
    # リダイレクトURLを取得する
    next_url = _get_next_url()

    if form.validate_on_submit():
        user = User.query.filter_by(tuid=form.user_id.data).first()
        if user is None or not PkgUserAuth.check_passwd_for_svcdb(form.user_id.data, form.password.data):
            flash('invalid user_id or password')
            return redirect(url_for('adm_login', user_id=form.user_id.data, next_url=next_url))
        login_user(user, False)
        session['last_login_user_id'] = form.user_id.data

        return set_cookie(StrUtil.get_safe_config(current_app, 'SVCDB_SYS_COOKIE'), current_user.tuid, 'adm_index')

    # ログイン情報を保持する
    last_login_user_id = StrUtil.get_safe_edit_mode('last_login_user_id', session)
    user_id = request.args.get('user_id') or last_login_user_id
    if user_id:
        form.user_id.data = user_id

    # システムメッセージ
    loginSystemMessage = ''
    systemMessage = SvcdbSystemMessage.getSystemMessage('LOGIN')
    if systemMessage is not None:
        loginSystemMessage = systemMessage.memo_txt
        if systemMessage.memo_format and systemMessage.memo_format == Const.HTML_FORMAT:
            loginSystemMessage = Markup(loginSystemMessage.replace('\n', '<br>'))

    return render_template(
        'svcdb_admin/login.html',
        form=form,
        next_url=next_url,
        loginSystemMessage=loginSystemMessage,
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
