# coding:utf-8
import os
import sys

from flaskr.lib.svcdb_lib.db_util import DbUtil

sys.path.append('/home04/svcdb/flask/svcdb/')
os.environ['NLS_LANG'] = 'JAPANESE_JAPAN.AL32UTF8'

from flaskr import create_app

app = create_app()
app.app_context().push()

# 入力チェックする
cname = [
    'id',
    'title',
    'body',
    'amount',
    'order_by',
    'created_by',
    'created_at',
]
input_value = [
    '1',
    'ああああああああああああああああああああああああああああああああああああああああ',
    'test body',
    '10.24',
    '1',
    'z02039n0',
    '2020-02-18',
]
db_field = [
    'ID',
    'TITLE',
    'BODY',
    'AMOUNT',
    'ORDER_BY',
    'CREATED_BY',
    'CREATED_AT',
]
col_prop = {'cname': cname, 'input_value': input_value, 'db_field': db_field}
param_prop = {'err_msgs': [], 'table_name': 'PYTHON_TEST001', 'col_prop': col_prop}
DbUtil.check_input_form_data_by_db(param_prop)

app.logger.debug(list(param_prop['err_msgs']))
