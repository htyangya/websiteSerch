# coding:utf-8
import os
import sys

from flaskr.lib.svcdb_lib.date_util import DateUtil
from flaskr.lib.svcdb_lib.num_util import NumUtil
from flaskr.lib.svcdb_lib.str_util import StrUtil

sys.path.append('/home04/svcdb/flask/svcdb/')
os.environ['NLS_LANG'] = 'JAPANESE_JAPAN.AL32UTF8'

from flaskr import create_app

app = create_app()
app.app_context().push()

# 日付チェック
rst = DateUtil.check_date_format('2020/02/18', 'YYYY/MM/DD')
app.logger.debug(rst)

# 日付チェック
rst = NumUtil.is_number_data('aa')
app.logger.debug(rst)
rst = NumUtil.is_integer_data('10.22')
app.logger.debug(rst)
num_prop = {'sign_ref': '', 'i_ref': '', 'f_ref': ''}
rst = NumUtil.split_number('10.22', num_prop)
app.logger.debug(rst)

rst = StrUtil.truncate('ああああああああああああああああああああああああああああああああああああああああああ', 20)
app.logger.debug(rst)