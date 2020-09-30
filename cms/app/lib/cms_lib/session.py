import urllib

# session 必須
from flask import session, request, make_response
from werkzeug.utils import redirect

from app import db
from app.controllers.common import CreateSeq
from app.lib.cms_lib.str_util import StrUtil
from app.models.cms_db_admin.cms_db import CmsDb
from app.models.cms_session_table import CmsSessionTable

current_db = None


def get_db_id():
    if request.method == 'POST':
        return request.form['db_id']
    else:
        return request.args.get('db_id', '')


def get_current_db(db_id):
    if not db_id:
        db_id = get_db_id()

    # システム情報を取得する
    return CmsDb.getCmsDbInfo(db_id)


def clean_current_db(self):
    # システム情報を削除する
    self.current_db = None


def set_cookie(session_cookie_name, tuid, redirectUrl):
    random_str = '{0}{1}'.format(StrUtil.make_random_str(25), str(CreateSeq.getSessionIdSeq()).zfill(9))

    StrUtil.print_debug('random_str:{}'.format(str(random_str)))
    cst = CmsSessionTable(session_cookie_name, random_str, tuid)
    db.session.add(cst)
    db.session.commit()

    if request.method == 'GET':
        next_url = request.args.get('next_url')
    else:
        next_url = request.form['next_url']

    if not next_url:
        next_url = redirectUrl
    else:
        next_url = urllib.parse.unquote(next_url)

    StrUtil.print_debug('next_url:{}'.format(str(next_url)))
    response = make_response(redirect(next_url))
    response.set_cookie(session_cookie_name, random_str)
    return response


def get_session_id(session_cookie_name):
    # セッションIDの取得
    return request.cookies.get(session_cookie_name)


def get_request_data(name):
    if request.method == "GET":
        return request.args.get(name)
    elif request.method == "POST":
        return request.args.get(name) or request.form.get(name)
