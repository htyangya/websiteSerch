import re
import sys
from datetime import date, datetime

from flask import current_app

from app.lib.cms_lib.arr_util import ArrUtil
from app.lib.cms_lib.str_util import StrUtil


class DateUtil:
    MoY = ['January', 'February', 'March', 'April', 'May', 'June',
           'July', 'August', 'September', 'October', 'November', 'December']
    MoYs = list(map(lambda x: x[0:3], MoY))

    def check_date_format(date_str, fmt):
        if not date_str:
            return 0

        date_hash = {}
        if DateUtil._get_ymd(date_str, fmt, date_hash) != 0 \
                or int(date_hash['yyyy']) < 1900 \
                or not DateUtil._check_date(date_hash['yyyy'], date_hash['mm'], date_hash['dd']):
            return 1

        return 0

    # FIXME: _get_ymdは配列を返すようにする
    #        errorのときはundefを返す
    #        check_date_formatで_get_ymdの使い方を見直す
    def _get_ymd(date_str, fmt, date_hash):
        if fmt == 'YYYY-MM-DD' or fmt == 'YYYY/MM/DD':
            match = re.search('^(\d+)[\-\/](\d+)[\-\/](\d+)$', date_str)
            if not match:
                return 1
            date_hash['yyyy'] = match.group(1)
            date_hash['mm'] = match.group(2)
            date_hash['dd'] = match.group(3)
        elif fmt == 'YY/MM/DD':
            match = re.search('^(\d{1,2})[\-\/](\d{1,2})[\-\/](\d{1,2})$', date_str)
            if not match:
                return 1
            if int(match.group(3)) > 50:
                date_hash['yyyy'] = 1900 + int(match.group(1))
            else:
                date_hash['yyyy'] = 2000 + int(match.group(1))
            date_hash['mm'] = match.group(2)
            date_hash['dd'] = match.group(3)
        elif fmt == 'DD/Mon/YY' or fmt == 'DD-Mon-YY':
            match = re.search('^(\d+)[\-\/](\w+)[\-\/](\d+)$', date_str)
            if not match:
                return 1
            if int(match.group(3)) > 50:
                date_hash['yyyy'] = 1900 + int(match.group(3))
            else:
                date_hash['yyyy'] = 2000 + int(match.group(3))
            date_hash['mm'] = ArrUtil.search_array(DateUtil.MoYs, match.group(2)) + 1
            date_hash['dd'] = match.group(1)

            if int(date_hash['mm']) <= 0:
                return 1
        elif fmt == 'DD/Mon/YYYY' or fmt == 'DD-Mon-YYYY':
            match = re.search('^(\d+)[\-\/](\w+)[\-\/](\d+)$', date_str)
            if not match:
                return 1
            date_hash['yyyy'] = int(match.group(3))
            date_hash['mm'] = ArrUtil.search_array(DateUtil.MoYs, match.group(2)) + 1
            date_hash['dd'] = match.group(1)

            if int(date_hash['mm']) <= 0:
                return 1
        else:
            StrUtil.print_debug("Invalid date format({})".format(fmt))
            sys.exit(1)

        return 0

    def _check_date(year, month, day):
        try:
            newDataStr = "%04d/%02d/%02d" % (int(year), int(month), int(day))
            newDate = datetime.datetime.strptime(newDataStr, "%Y/%m/%d")
            return True
        except Exception as e:
            tb = sys.exc_info()[2]
            StrUtil.print_error("_check_date error_msg:{}".format(str(e.with_traceback(tb))))
            return False

    @staticmethod
    def current_date_str():
        dt_now = datetime.now()
        return dt_now.strftime('%Y%m%d%H%M%S')

    @staticmethod
    # json date, datetimeの変換関数
    def json_serial(obj):
        # 日付型の場合には、文字列に変換します
        if isinstance(obj, (datetime, date)):
            return obj.strftime(StrUtil.get_safe_config(current_app, 'STRFTIME_TIME_FORMAT'))
        raise TypeError("Type %s not serializable" % type(obj))
