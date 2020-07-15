# coding:utf-8
import os
import sys

sys.path.append('/home03/cms/flask/cms/')
os.environ['NLS_LANG'] = 'JAPANESE_JAPAN.AL32UTF8'

from app import create_app
from app.lib.cms_lib.ctx_util import CtxUtil

app = create_app()
app.app_context().push()

ctxUtil = CtxUtil()
ctxUtil.optimize_ctx(app)
