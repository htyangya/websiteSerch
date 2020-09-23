import random
import string
import unicodedata

from flask import request, current_app
from numpy import unicode

from app.lib.conf.const import Const


class HtmlUtil:
    @staticmethod
    def print_spacer(css_class_name='border'):
        return f'<div class="{css_class_name}"></div>'

    def print_html_head(len):
        return ''.join(random.choices(string.ascii_letters + string.digits + '/', k=len))

    @staticmethod
    def print_navi_bar(navi_arr_ref):
        html = HtmlUtil.print_spacer()

        while len(navi_arr_ref) > 0:
            html += '&nbsp;&gt;&nbsp;'
            name = navi_arr_ref.pop(0)
            if len(navi_arr_ref) > 0:
                link = navi_arr_ref.pop(0)
                if link is None or link == "":
                    html += name
                else:
                    html += f"<a href=\"{link}\">{name}</a>"
            else:
                html += name

        html += HtmlUtil.print_spacer()
        return html

    @staticmethod
    def get_browser(request):
        user_agent = request.environ['HTTP_USER_AGENT'].lower()

        if 'opera' in user_agent:
            return 'opera'
        elif 'msie' in user_agent:
            return 'ie'
        elif 'trident/7.0' in user_agent:
            return 'ie11'
        elif 'edg' in user_agent:
            return 'edg'
        elif 'chrome' in user_agent:
            return 'chrome'
        elif 'safari' in user_agent:
            return 'safari'
        elif 'gecko' in user_agent:
            return 'gecko'
        else:
            return ''