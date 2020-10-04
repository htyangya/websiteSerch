import math
import re
import sys
import threading
from concurrent.futures.thread import ThreadPoolExecutor
from io import BytesIO
import pandas as pd
import pytesseract
import requests as rq
from PIL import Image
from pyquery import PyQuery as pq
from requests import ConnectTimeout
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
        self.prepare_data()
        task_args = self.df.index.to_list()[:50]
        self.count = len(task_args)
        executor = ThreadPoolExecutor(max_workers=min(config.get_global_setting("thread_count"), self.count))
        result = executor.map(self.search_one, task_args)
        print("任务已开始")
        print(list(result))

    def prepare_data(self):
        try:
            response = rq.get(self.url, timeout=self.timeout)
            html = response.content.decode(self.charset)
            doc = pq(html)
            inputs = doc("#frmIndex input")
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
        except ConnectTimeout:
            raise Exception("该查询网址链接有问题，{0}秒钟内未有效连接，请确认网络情况".format(self.timeout))

    def read_excel(self, file):
        df = pd.read_excel(file, dtype=str, engine="openpyxl")
        df.columns = df.columns.to_series().str.strip()
        df = df.loc[~df.isna().all(1)].fillna("")
        if len(df) == 0:
            raise Exception("该excel文件中没有数据！")
        inputs_dict = self.inputs_dict
        for html_name, excel_name in inputs_dict.items():
            if excel_name != "验证码" and excel_name not in df.columns:
                raise Exception("该excel文件不适合此策略器，excel列中缺乏必要的列：{0}".format(excel_name))
        self.df = df

    def search_one(self, index):
        repeat_count = 0
        data = self.make_data(index)
        print(index)
        while True:
            try:
                if self._cancel:
                    return self.get_search_data(index) + ["任务已手动取消"] * len(self.results_select)
                response = rq.post(self.url, data=data, **self.send_args)
                if response.status_code == 200:
                    html = response.content.decode(self.charset)
                    doc = pq(html)
                    self.task_done()
                    self.show_process("完成度", self.finish_count, self.count)
                    return self.get_search_data(index) + [doc(select).text() for select in self.results_select]
            except ConnectTimeout:
                # 重新查询,直到超出最大重复次数
                repeat_count += 1
                if repeat_count > self.max_repeat_count:
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
                # Image.open(BytesIO(response.content)).show()
                # print(vcode)
                return vcode

    def _test_vcode(self, vcode):
        print(vcode)
        if len(vcode) != self.vcode_len:
            return False
        data = self.make_data(0, vcode)
        response = rq.post(self.url, data=data, **self.send_args)
        html = response.content.decode(self.charset)
        print(self.vcode_error in html)
        if self.vcode_error in html:
            return False
        # print(pq(html)("#frmIndex > script").text())
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
        df.to_excel("result.xlsx", index=False)

    def cancel(self):
        self._cancel = True

    def task_done(self):
        with self.cond:
            self.finish_count += 1

    @property
    def send_args(self):
        return {
            "headers": self.headers,
            "cookies": self.cookies,
            "timeout": self.timeout
        }

    @staticmethod
    def show_process(desc_text, curr, total):
        proc = math.ceil(curr / total * 100)
        show_line = '\r' + desc_text + ':' + '>' * proc \
                    + ' ' * (100 - proc) + '[%s%%]' % proc \
                    + '[%s/%s]' % (curr, total)
        sys.stdout.write(show_line)
        sys.stdout.flush()
