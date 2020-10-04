import math
import os
import re
import threading
from concurrent.futures.thread import ThreadPoolExecutor
from io import BytesIO

import pandas as pd
import pytesseract
import requests as rq
from PIL import Image
from pyquery import PyQuery as pq
from requests import ConnectTimeout, Timeout, ReadTimeout, ConnectionError
from urlobject import URLObject

import config


class Search:
    timeout = config.get_global_setting("timeout")
    max_repeat_count = config.get_global_setting("max_repeat_count")

    def __init__(self, url, strategy_name):
        self.headers = {
            'User-Agent': config.get_global_setting("user_agent"),
        }
        self.count = 0
        self.url = URLObject(url)
        self.strategy_name = strategy_name
        self.finish_count = 0
        self._cancel = False
        self.cond = threading.Condition()
        self.charset = config.auto_get_charset(url)
        self.vcode_len = config.get_websites_setting(self.url.hostname, "vcode_len")
        self.vcode_error = config.get_strategy_setting(self.strategy_name, "vcode_error")
        self.inputs_dict = config.get_strategy_inputs(self.strategy_name)
        results_list = config.get_strategy_setting(self.strategy_name, "results")
        self.results_select = [select for col_name, select in results_list]
        self.results_colname = [col_name for col_name, select in results_list]
        self.search_colname = None
        self.cookies = None
        self.hidden_data = None
        self.required_inputs = None
        self.img_url = None
        self.vcode = None
        self.df = None

    def start(self):
        task_args = self.df.index.to_list()
        executor = ThreadPoolExecutor(max_workers=min(config.get_global_setting("thread_count"), self.count))
        result = executor.map(self.search_one, task_args)
        self.write_result(list(result))

    def prepare_data(self):
        try:
            response = rq.get(self.url, timeout=self.timeout)
            html = self.parse_response(response)
            doc = pq(html)
            inputs = doc("{} input".format(config.get_strategy_setting(self.strategy_name, "form_select")))
            hidden_data = {i.attr("name"): i.val().encode(self.charset) for i in inputs.items() if
                           i.attr("type").lower() in ["hidden", "submit"]}
            required_inputs = [i.attr("name") for i in inputs.items() if
                               i.attr("type").lower() not in ["hidden", "submit"]]
            self._check_data(required_inputs)
            # 保存查回来的cookie，隐藏input，需要输入的input，验证码的url链接，查到的第一个验证码
            self.cookies = rq.utils.dict_from_cookiejar(response.cookies)
            self.hidden_data = hidden_data
            self.required_inputs = required_inputs
            self.img_url = self.url.relative(
                doc(config.get_strategy_setting(self.strategy_name, "vcode_image")).attr("src"))
            self.vcode = self._get_vcode()
        except (ConnectTimeout, Timeout, ReadTimeout, ConnectionError):
            raise Exception("该查询网址链接有问题，{0}秒钟内未有效连接，请确认网络情况".format(self.timeout))

    def parse_response(self, response):
        return response.content.decode(self.charset, errors="ignore")

    def read_excel(self, file):
        df = pd.read_excel(file, dtype=str, engine="openpyxl")
        df.columns = df.columns.to_series().str.strip()
        df = df.loc[~df.isna().all(1)].fillna("")
        length = len(df)
        if length == 0:
            raise Exception("该excel文件中没有数据！")
        inputs_dict = self.inputs_dict
        self.count = length
        for html_name, excel_name in inputs_dict.items():
            if excel_name != "验证码" and excel_name not in df.columns:
                raise Exception("该excel文件不适合此策略器，excel列中缺乏必要的列：{0}".format(excel_name))
        self.df = df

    def search_one(self, index):
        repeat_count = 0
        data = self.make_data(index)
        while True:
            try:
                if self._cancel:
                    self.task_done()
                    return self.get_search_data(index) + ["任务已手动取消"] * len(self.results_select)
                response = rq.post(self.url, data=data, **self.send_args)
                if response.status_code == 200:
                    html = self.parse_response(response)
                    doc = pq(html)
                    self.task_done()
                    return self.get_search_data(index) + [doc(select).text() for select in self.results_select]
            except (ConnectTimeout, Timeout, ReadTimeout, ConnectionError):
                # 重新查询,直到超出最大重复次数
                repeat_count += 1
                if repeat_count >= self.max_repeat_count:
                    self.task_done()
                    return self.get_search_data(index) + ["网络不好，超出最大重复次数，任务已自动取消"] * len(self.results_select)

    def _check_data(self, required_inputs: list):
        inputs_html_names = self.inputs_dict.keys()
        for i in required_inputs:
            if i not in inputs_html_names:
                raise Exception("配置文件中inputs项缺乏必要参数：{0}".format(i))

    def _get_vcode(self):
        while True:
            response = rq.get(self.img_url, **self.send_args)
            vcode = pytesseract.image_to_string(Image.open(BytesIO(response.content)))
            vcode = re.sub("\D+", "", vcode)
            if self._test_vcode(vcode):
                return vcode

    def _test_vcode(self, vcode):
        if len(vcode) != self.vcode_len:
            return False
        data = self.make_data(0, vcode)
        response = rq.post(self.url, data=data, **self.send_args)
        html = self.parse_response(response)
        if self.vcode_error in html:
            return False
        return True

    def make_data(self, index, vcode=""):
        required_data = {}
        search_colname = []
        for input_name in self.required_inputs:
            excel_name = self.inputs_dict.get(input_name)
            if excel_name == "验证码":
                data = vcode or self.vcode
            else:
                search_colname.append(excel_name)
                data = self.df.at[index, excel_name].strip().encode(self.charset)
            required_data[input_name] = data
        if self.search_colname is None:
            self.search_colname = search_colname
        return dict(**self.hidden_data, **required_data)

    def get_search_data(self, index):
        return [self.df.at[index, self.inputs_dict.get(input_name)].strip() for input_name in self.required_inputs if
                self.inputs_dict.get(input_name) != "验证码"]

    def write_result(self, result):
        df = pd.DataFrame(result, columns=self.search_colname + self.results_colname)
        file_name = "result.xlsx"
        i = 0
        while os.path.exists(file_name):
            i += 1
            file_name = "result{}.xlsx".format(i)
        df.to_excel(file_name, index=False)

    def cancel(self):
        self._cancel = True

    def task_done(self):
        with self.cond:
            self.finish_count += 1

    def is_finish(self):
        return self.finish_count >= self.count

    @property
    def send_args(self):
        return {
            "headers": self.headers,
            "cookies": self.cookies,
            "timeout": self.timeout
        }

    @staticmethod
    def get_process_text(desc_text, curr, total):
        proc = math.ceil(curr * 100 / total)
        char_count = math.ceil(curr * 40 / total)
        show_line = desc_text + ':' + '>' * char_count + '#' * (40 - char_count) + '[%s%%]' % proc + '[%s/%s]' % (
            curr, total)
        return show_line
