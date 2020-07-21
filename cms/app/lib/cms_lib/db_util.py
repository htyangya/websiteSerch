import re
import sys

from sqlalchemy import text

from app import db
from app.lib.cms_lib.date_util import DateUtil
from app.lib.cms_lib.num_util import NumUtil
from app.lib.cms_lib.str_util import StrUtil
from app.lib.conf.const import Const


class DbUtil:
    def check_input_form_data_by_prop(param_prop):
        err_msgs = []
        try:
            if 'form' not in param_prop:
                err_msgs.append(Const.INVALID_PARAM_ERR_MSG)
                param_prop['err_msgs'].extend(err_msgs)
                return

            form = param_prop['form']
            for pro in param_prop['pro_list']:
                property_type = pro.get("property_type")
                if "KEYWORD" == property_type:
                    continue

                col_name = pro.get("db_column_name").lower()
                value = form.__dict__[col_name].data
                if col_name.startswith("num_"):
                    if len(value) > 0:
                        value = int(value)
                    else:
                        value = ''

                # 必須チェック
                if pro.get("nullable") == 'FALSE' and not value:
                    err_msgs.append(Const.REQUIRED_MSG.format(pro.get("property_name")))
                    continue

                if not value:
                    continue

                # 数字チェック
                if "NUMBER" == property_type:
                    if NumUtil.is_number_data(value) != 1:
                        err_msgs.append(
                            Const.NUMERICAL_VALUE_REQUIRED_MSG.format(pro.get("property_name")))
                    else:
                        num_prop = {'sign_ref': '', 'i_ref': '', 'f_ref': ''}
                        NumUtil.split_number(value, num_prop)
                        if len(num_prop['i_ref']) > int(pro.get("i_len")):
                            err_msgs.append(
                                Const.INTEGRAL_PART_OUT_OF_RANGE_MSG.format(
                                    pro.get("property_name"),
                                    str(pro.get("i_len"))))
                        if len(num_prop['f_ref']) > int(pro.get("f_len")):
                            err_msgs.append(
                                Const.FRACTIONAL_PART_OUT_OF_RANGE_MSG.format(
                                    pro.get("property_name"),
                                    str(pro.get("f_len"))))

                # 日付チェック
                elif 'DATE' == property_type:
                    if DateUtil.check_date_format(value, Const.DATE_FORMAT) != 0:
                        err_msgs.append(
                            Const.AVAILABLE_DATE_REQUIRED_MSG.format(
                                pro.get("property_name"), value))

                # 文字列チェック
                elif 'TEXT' == property_type or 'TEXT_MULTILINE' == property_type:
                    # 桁数チェック
                    if pro.get("data_size"):
                        if StrUtil.lenb(value) > int(pro.get("data_size")):
                            err_msgs.append(
                                Const.LENGTH_OVER_MSG.format(
                                    pro.get("property_name"), str(pro.get("data_size"))))

                # バリデータチェック（正式表現）
                re_cond = pro.get('validate_rule')
                if re_cond and len(value) > 0:
                    try:
                        if not re.search(re_cond, value):
                            err_msgs.append(pro.get('validate_err_msg').replace('<#DATA#>', value))
                    except Exception as e:
                        tb = sys.exc_info()[2]
                        StrUtil.print_error('check_input_form_data_by_prop validate_rule:{} error_msg:{}'.format(
                            re_cond, str(e.with_traceback(tb))))
            param_prop['err_msgs'].extend(err_msgs)

        except Exception as e:
            tb = sys.exc_info()[2]
            param_prop['err_msgs'].extend(str(e.with_traceback(tb)))
            StrUtil.print_error('check_input_form_data_by_prop error_msg:{}'.format(str(e.with_traceback(tb))))

    def check_input_form_data_by_db(param_prop):
        err_msgs = []
        try:
            if 'table_name' not in param_prop \
                    or 'col_prop' not in param_prop:
                err_msgs.append(Const.INVALID_PARAM_ERR_MSG)
                param_prop['err_msgs'].extend(err_msgs)
                return

            col_prop = param_prop['col_prop']
            if 'cname' not in col_prop \
                    or 'input_value' not in col_prop \
                    or 'db_field' not in col_prop:
                err_msgs.append(Const.INVALID_PARAM_ERR_MSG)
                param_prop['err_msgs'].extend(err_msgs)
                return

            user_tab_columns = DbUtil.get_user_tab_columns_hash(param_prop['table_name'])

            for idx in range(0, len(col_prop['cname'])):
                value = col_prop['input_value'][idx]
                db_field = col_prop['db_field'][idx]

                # 必須チェック
                if 'nullable' in user_tab_columns[db_field]:
                    if user_tab_columns[db_field]['nullable'] == 'N' and not value:
                        err_msgs.append(Const.REQUIRED_MSG.format(col_prop['cname'][idx]))
                        continue

                if not value:
                    continue

                if 'data_type' in user_tab_columns[db_field] and 'data_length' in user_tab_columns[db_field]:
                    data_type = user_tab_columns[db_field]['data_type']
                    data_length = user_tab_columns[db_field]['data_length']

                    # 文字列チェック
                    if data_type == 'VARCHAR2' or data_type == 'CHAR':
                        # 桁数チェック
                        if StrUtil.lenb(value) > int(data_length):
                            err_msgs.append(
                                Const.LENGTH_OVER_MSG.format(col_prop['cname'][idx], str(data_length)))

                    # 数字チェック
                    elif data_type == 'NUMBER':
                        """
                        if re.search(',', str(data_length)):
                            t = value
                            t = re.sub(r'[^\.]', r'', t)
                            if len(t) > 1 or re.search('[^0-9^\.]', value):
                                err_msgs.append(
                                    Const.NUMERICAL_VALUE_REQUIRED_MSG.format(col_prop['cname'][idx]))
                        else:
                            if re.search('[^0-9]', value):
                                err_msgs.append(
                                    Const.INTEGER_VALUE_REQUIRED_MSG.format(col_prop['cname'][idx]))
                        """
                        if NumUtil.is_number_data(value) != 1:
                            err_msgs.append(
                                Const.NUMERICAL_VALUE_REQUIRED_MSG.format(col_prop['cname'][idx]))
                        else:
                            num_prop = {'sign_ref': '', 'i_ref': '', 'f_ref': ''}
                            NumUtil.split_number(value, num_prop)
                            if 'data_precision' in user_tab_columns[db_field] \
                                    and user_tab_columns[db_field]['data_precision'] is not None:
                                if len(num_prop['i_ref']) > int(user_tab_columns[db_field]['data_precision']):
                                    err_msgs.append(
                                        Const.INTEGRAL_PART_OUT_OF_RANGE_MSG.format(
                                            col_prop['cname'][idx],
                                            str(user_tab_columns[db_field]['data_precision'])))
                            if 'data_scale' in user_tab_columns[db_field] \
                                    and user_tab_columns[db_field]['data_scale'] is not None:
                                if len(num_prop['f_ref']) > int(user_tab_columns[db_field]['data_scale']):
                                    err_msgs.append(
                                        Const.FRACTIONAL_PART_OUT_OF_RANGE_MSG.format(
                                            col_prop['cname'][idx],
                                            str(user_tab_columns[db_field]['data_scale'])))

                    # 日付チェック
                    elif data_type == 'DATE':
                        if DateUtil.check_date_format(value, Const.DATE_FORMAT) != 0:
                            err_msgs.append(
                                Const.AVAILABLE_DATE_REQUIRED_MSG.format(col_prop['cname'][idx], value))

                    # 文字列「CLOB」チェック
                    elif data_type == 'CLOB':
                        if len(value) > 10 * 1024:
                            err_msgs.append(
                                Const.LENGTH_OVER_MSG.format(col_prop['cname'][idx], '10,000'))

            param_prop['err_msgs'].extend(err_msgs)

        except Exception as e:
            tb = sys.exc_info()[2]
            param_prop['err_msgs'].extend(str(e.with_traceback(tb)))
            StrUtil.print_error('check_input_form_data_by_db error_msg:{}'.format(str(e.with_traceback(tb))))

    # 使用していない、削除予定
    def check_input_form_data_by_db2(param_prop):
        err_msgs = []
        try:
            if 'form' not in param_prop \
                    or 'table_name' not in param_prop \
                    or 'col_prop' not in param_prop:
                err_msgs.append(Const.INVALID_PARAM_ERR_MSG)
                param_prop['err_msgs'] = err_msgs
                return

            col_prop = param_prop['col_prop']
            if 'cname' not in col_prop \
                    or 'input_field' not in col_prop \
                    or 'db_field' not in col_prop:
                err_msgs.append(Const.INVALID_PARAM_ERR_MSG)
                param_prop['err_msgs'] = err_msgs
                return

            form = param_prop['form']
            user_tab_columns = DbUtil.get_user_tab_columns_hash(param_prop['table_name'])

            for idx in range(0, len(col_prop['cname'])):

                input_field = col_prop['input_field'][idx]
                value = str(form.__dict__[input_field].data)
                db_field = col_prop['db_field'][idx]

                # 必須チェック
                if 'nullable' in user_tab_columns[db_field]:
                    if user_tab_columns[db_field]['nullable'] == 'N' and not value:
                        err_msgs.append(Const.REQUIRED_MSG.format(col_prop['cname'][idx]))

                # 桁数チェック
                if 'data_type' in user_tab_columns[db_field] and 'data_length' in user_tab_columns[db_field]:
                    data_type = user_tab_columns[db_field]['data_type']
                    data_length = user_tab_columns[db_field]['data_length']
                    if data_type == 'VARCHAR2' or data_type == 'CHAR':
                        if StrUtil.lenb(value) > int(data_length):
                            err_msgs.append(
                                Const.LENGTH_OVER_MSG.format(col_prop['cname'][idx], str(data_length)))
                    elif data_type == 'NUMBER':
                        if re.search(',', str(data_length)):
                            t = value
                            t = re.sub(r'[^\.]', r'', t)
                            if len(t) > 1 or re.search('[^0-9^\.]', value):
                                err_msgs.append(
                                    Const.NUMERICAL_VALUE_REQUIRED_MSG.format(col_prop['cname'][idx]))
                        else:
                            if re.search('[^0-9]', value):
                                err_msgs.append(
                                    Const.INTEGER_VALUE_REQUIRED_MSG.format(col_prop['cname'][idx]))
                    elif data_type == 'DATE':
                        if DateUtil.check_date_format(value, Const.DATE_FORMAT) != 0:
                            err_msgs.append(
                                Const.AVAILABLE_DATE_REQUIRED_MSG.format(col_prop['cname'][idx], value))

            param_prop['err_msgs'] = err_msgs

        except Exception as e:
            tb = sys.exc_info()[2]
            param_prop['err_msgs'] = str(e.with_traceback(tb))
            StrUtil.print_error('check_input_form_data_by_db error_msg:{}'.format(str(e.with_traceback(tb))))

    def get_user_tab_columns_hash(table_name):
        selectSql = '''
            SELECT T.COLUMN_NAME, T.DATA_TYPE, T.DATA_LENGTH, T.NULLABLE, T.DATA_PRECISION, T.DATA_SCALE
            FROM USER_TAB_COLUMNS T
            WHERE TABLE_NAME = :table_name
        '''
        t = text(selectSql)
        rst = db.session.execute(t, {'table_name': table_name})

        dic = {}
        for row in rst:
            dic = {**dic, **{row['column_name']: row}}

        return dic

