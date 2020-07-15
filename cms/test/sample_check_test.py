# coding:utf-8
import os
import sys

from app.lib.cms_lib.date_util import DateUtil
from app.lib.cms_lib.num_util import NumUtil
from app.lib.cms_lib.str_util import StrUtil

sys.path.append('/home03/cms/flask/cms/')
os.environ['NLS_LANG'] = 'JAPANESE_JAPAN.AL32UTF8'

from app import create_app

app = create_app()
app.app_context().push()

# 日付チェック
rst = DateUtil.check_date_format('2020/02/18', 'YYYY/MM/DD')
StrUtil.print_debug(rst)

# 日付チェック
rst = NumUtil.is_number_data('aa')
StrUtil.print_debug(rst)
rst = NumUtil.is_integer_data('10.22')
StrUtil.print_debug(rst)
num_prop = {'sign_ref': '', 'i_ref': '', 'f_ref': ''}
rst = NumUtil.split_number('10.22', num_prop)
StrUtil.print_debug(rst)

rst = StrUtil.truncate('ああああああああああああああああああああああああああああああああああああああああああ', 20)
StrUtil.print_debug(rst)