import random
import string
import unicodedata

from flask import request, current_app
from numpy import unicode

from app.lib.conf.const import Const


class StrUtil:
    def make_random_str(len):
        return ''.join(random.choices(string.ascii_letters + string.digits + '/', k=len))

    def get_safe_config(app, param_name):
        if not param_name:
            return ''

        if param_name in app.config:
            return app.config[param_name]

        return ''

    def get_safe_string(param_value):
        if not param_value:
            return ''

        return param_value

    def get_safe_edit_mode(session_name, session):
        if not session_name:
            return False

        if session_name in session:
            return session[session_name]

        return False

    def trim(value):
        return unicode(value).strip()

    def truncate(value, num_bytes):
        while StrUtil.lenb(value) > num_bytes:
            value = value[:-1]
        return value

    def lenb(message):
        # 文字列長カウント用の変数を定義
        text_length = 0
        # 文章中の文字数分ループを回す
        for i in message:
            c = unicodedata.east_asian_width(i)
            # 半角
            if c == 'H' or c == 'Na':
                text_length = text_length + 1
            # 全角
            elif c == 'F' or c == 'A' or c == 'W':
                text_length = text_length + 3
            # 半角
            else:
                text_length = text_length + 1
        return text_length

    @staticmethod
    def get_ip_addr():
        remote_addr = StrUtil.get_safe_config(current_app, 'LOCAL_REMOTE_ADDR')
        if not remote_addr:
            # define your own set
            trusted_proxies = {'127.0.0.1'}
            route = request.access_route + [request.remote_addr] + request.access_route
            remote_addr = next((addr for addr in reversed(route)
                                if addr not in trusted_proxies), request.remote_addr)
            StrUtil.print_debug("get_ip_addr remote_addr:{}".format(remote_addr))
        return remote_addr

    def print_debug(msg):
        is_debug_mode = StrUtil.get_safe_config(current_app, 'DEBUG')
        if is_debug_mode:
            current_app.logger.debug(Const.DEBUG_MSG_FORMAT.format(msg))

    def print_error(err_msg, exc_info=True):
        current_app.logger.error(Const.ERROR_MSG_FORMAT.format(err_msg), exc_info=exc_info)

    @staticmethod
    def get_current_url(error_cd=""):
        url = request.url
        if Const.LOGIN_ERROR == error_cd:
            url = request.base_url
        return url
