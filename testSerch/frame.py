import os
import threading
import time
import tkinter as tk
from tkinter import ttk
import config
from request_send import Search
from tkinter import messagebox


class PyWinDesign:
    def __init__(self, frame):
        self.frame = frame
        self.frame.title("欢迎使用网页查询系统 Author@yangya")
        self.frame.resizable(width=False, height=False)
        screenwidth = self.frame.winfo_screenwidth()
        screenheight = self.frame.winfo_screenheight()
        size = '%dx%d+%d+%d' % (513, 268, (screenwidth - 513) / 2, (screenheight - 268) / 2)
        self.frame.geometry(size)
        # 文件
        self.file_lable = tk.Label(self.frame, textvariable=tk.StringVar(value="文件"))
        self.file_lable.place(x=52, y=31, width=86, height=24)

        file_list = [file for file in os.listdir("xlsx") if file.endswith(".xlsx")]
        self.file = ttk.Combobox(self.frame, values=file_list, state='readonly')
        if len(file_list) > 0:
            self.file.current(0)
        self.file.bind("<<ComboboxSelected>>", self.on_file_select)
        self.file.place(x=144, y=35, width=290, height=20)
        # 策略器
        self.strategy_lable = tk.Label(self.frame, textvariable=tk.StringVar(value='策略器'))
        self.strategy_lable.place(x=53, y=66, width=86, height=24)

        strategy_names = config.get_strategy_names()
        self.strategy = ttk.Combobox(self.frame, values=strategy_names, state='readonly')
        if len(strategy_names) > 0:
            self.strategy.current(0)
        self.strategy.place(x=144, y=70, width=290, height=20)
        self.strategy.bind("<<ComboboxSelected>>", self.on_strategy_select)

        # url
        self.url_lable = tk.Label(self.frame, textvariable=tk.StringVar(value='查询网址'))
        self.url_lable.place(x=53, y=106, width=86, height=24)

        self.url = tk.Entry(self.frame)
        self.url.place(x=144, y=106, width=290, height=20)

        # 按钮
        self.button_title = tk.StringVar(value='开始查询')
        self.button = tk.Button(self.frame, textvariable=self.button_title,  # state='disabled',
                                command=self.button_Left_click)
        self.button.place(x=346, y=143, width=146, height=27)
        # 状态栏
        self.status_title = tk.StringVar(value='状态:可用')
        self.status = tk.Label(self.frame, textvariable=self.status_title)
        self.status.place(x=21, y=227, width=478, height=34)
        # 进度条
        self.bar_title = tk.StringVar(value="")
        self.bar = tk.Label(self.frame, textvariable=self.bar_title, anchor=tk.W)
        self.bar.place(x=21, y=178, width=478, height=34)

        self.search = None

    def button_Left_click(self):
        if self.button_title.get() == "开始查询":
            self.start()
        else:
            self.log("取消中，请稍后...")
            self.button["state"] = tk.DISABLED
            self.search.cancel()

    def start(self):
        file = self.file.get()
        strategy = self.strategy.get()
        url = self.url.get()
        if not file or not strategy or not url:
            self.error("请将所有必填项都选择或填写完毕！")
            return
        file = os.path.join("xlsx", file)
        search = Search(url, strategy)
        try:
            search.read_excel(file)
            search.prepare_data()
        except Exception as e:
            self.error(e)
            return
        self.search = search
        self.button_title.set("停止")
        self.file["state"] = tk.DISABLED
        self.url["state"] = tk.DISABLED
        self.strategy["state"] = tk.DISABLED
        self.log("正在查询中...")
        threading.Thread(target=search.start).start()
        threading.Thread(target=self.progress_show).start()

    def on_strategy_select(self, event):
        self.log("已经选择策略器: " + self.strategy.get()+"\n 点击[开始查询]，开始测试网络连接并获取第一个验证码")

    def on_file_select(self, event):
        pass

    def log(self, text):
        self.status_title.set(text)

    def error(self, text):
        messagebox.showerror(message=text)

    def bar_log(self, text):
        self.bar_title.set(text)

    def progress_show(self):
        while True:
            if not self.search._cancel:
                self.bar_log(Search.get_process_text("查询进度", self.search.finish_count, self.search.count))
            else:
                self.bar_log("")
            time.sleep(0.2)
            if self.search.is_finish():
                self.bar_log("")
                self.button_title.set("开始查询")
                self.button['state'] = tk.NORMAL
                self.file["state"] = tk.NORMAL
                self.url["state"] = tk.NORMAL
                self.strategy["state"] = tk.NORMAL
                self.log("已成功取消！" if self.search._cancel else "查询完毕！")
                messagebox.showinfo(message="查询完毕，请在该文件目录下查看result.xlsx文件！")
                return


if __name__ == '__main__':
    root = tk.Tk()
    root.iconbitmap("search.ico")
    app = PyWinDesign(root)
    root.mainloop()
