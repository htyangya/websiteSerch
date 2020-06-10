import urllib

from flask import session, request, make_response, url_for
from werkzeug.utils import redirect

from flaskr import db
from flaskr.controllers.common import CreateSeq
from flaskr.lib.svcdb_lib.str_util import StrUtil
from flaskr.models.svcdb_db import SvcdbDb
from flaskr.models.svcdb_session_table import SvcdbSessionTable

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
    return SvcdbDb.getSvcdbDbInfo(db_id)


def clean_current_db(self):
    # システム情報を削除する
    self.current_db = None


def set_cookie(session_cookie_name, tuid, redirectUrl):
    random_str = '{0}{1}'.format(StrUtil.make_random_str(25), str(CreateSeq.getSessionIdSeq()).zfill(9))

    StrUtil.print_debug('##########random_str:' + random_str)
    cst = SvcdbSessionTable(session_cookie_name, random_str, tuid)
    db.session.add(cst)
    db.session.commit()

    if request.method == 'GET':
        next_url = request.args.get('next_url')
    else:
        next_url = request.form['next_url']

    if not next_url:
        next_url = url_for(redirectUrl)
    else:
        next_url = urllib.parse.unquote(next_url)

    StrUtil.print_debug('next_url:' + next_url)
    response = make_response(redirect(next_url))
    response.set_cookie(session_cookie_name, random_str)
    return response


def get_session_id(session_cookie_name):
    # セッションIDの取得
    return request.cookies.get(session_cookie_name)
