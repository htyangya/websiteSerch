# coding:utf-8
import os
import sys

sys.path.append('/home04/svcdb/flask/svcdb/')
os.environ['NLS_LANG'] = 'JAPANESE_JAPAN.AL32UTF8'

from flaskr import create_app
from flaskr.lib.svcdb_lib.ctx_util import CtxUtil

app = create_app()
app.app_context().push()

ctxUtil = CtxUtil()
ctxUtil.reset_ctx_index()