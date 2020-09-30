import json
import re
import requests as rq
from pyquery import PyQuery as pq
from urlobject import URLObject
from PIL import Image
from requests import ConnectTimeout
from io import BytesIO

path = ""
url = "http://pta.guizhou.gov.cn/gwycj/GzCjcx/GzSearch.aspx?examSort=01&examDate=1&examName=2020%u9a9e%u78cb%u5439%u5bb8%u70b5%u6e37%u934f%ue100%u59df%u935b%u6a48%u7d19%u6d5c%u70d8%u76af%u7480%ufe40%u7642%u951b%u590b%u5ad1%u8930%u66e0%u746a%u7487%u66df%u579a%u7f01%u2542%u5e13%u935a%3f"
image_url = "gif.aspx"
action = "./GzSearch.aspx?examSort=01&examDate=1&examName=2020%u9a9e%u78cb%u5439%u5bb8%u70b5%u6e37%u934f%ue100%u59df%u935b%u6a48%u7d19%u6d5c%u70d8%u76af%u7480%ufe40%u7642%u951b%u590b%u5ad1%u8930%u66e0%u746a%u7487%u66df%u579a%u7f01%u2542%u5e13%u935a%3f"



def get(image_url, action):
    try:
        s = rq.Session()
        s.headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 Edg/85.0.564.63'

        }
        rr=s.get(url, timeout=5)
        print(rr.encoding)
        imr=s.get(image_url, timeout=15)
        image = Image.open(BytesIO(imr.content))
        image.show()
        yzm = input("请输入验证码:")
        data = {
            "TxtName": "洪维",
            "TxtHaoMa": "10224133302",
            "txtJym": yzm,
            "__VIEWSTATE": "/wEPDwUKMTAwMzgzOTg0Ng9kFgICAw9kFgICAQ9kFgQCAQ9kFgYCAQ8PFgIeBFRleHQFYjIwMjDpqp7no4vlkLnlrrjngrXmuLfpjY/uhIDlp5/pjZvmqYjntJnmtZzng5jnmq/nkoDvuYDnmYLplJvlpIvlq5HopLDmm6Dnkarnkofmm5/lnprnvIHilYLluJPpjZo/ZGQCBw8PFgIfAAUP5YeG6ICD6K+B5Y+377yaZGQCEQ8PZBYCHgdvbmNsaWNrBRpKYXZhc2NyaXB0OnJldHVybiBjaGVjaygpO2QCAw8PFgIeB1Zpc2libGVoZBYGAgEPDxYCHwAFYjIwMjDpqp7no4vlkLnlrrjngrXmuLfpjY/uhIDlp5/pjZvmqYjntJnmtZzng5jnmq/nkoDvuYDnmYLplJvlpIvlq5HopLDmm6Dnkarnkofmm5/lnprnvIHilYLluJPpjZo/ZGQCAw88KwARAgAPFgIfAmhkDBQrAABkAgUPDxYCHwJnZGQYAQUJR3JpZFZpZXcxD2dkP1+WXklNZrMI8Kgk4na4JgqAwxIjVd4qKF1ZOwfrVHA=",
            "__VIEWSTATEGENERATOR": "AA59DA6E",
            "__EVENTVALIDATION": "/wEdAAWzKB3ewsjUs+nC6x7ILKlJvqpQkv2FJlCd366NAvz8uR/0J+7A+X+rVovkFDt+4BZKZ5fmGEq5xI7G200hjm3wPOaW1pQztoQA36D1w/+bXd8b5jE3/iVt8vZwb3N4VrxzJu0SwQeH5Xt79JuP8qZ1",
            "btnSubmit": "查　询",
        }
        response = s.post(action, data=data, timeout=5, headers={"Referer":url})
        open("re.html", "wb").write(response.content)
        print(response.status_code, response.encoding)
        if response.status_code == 200:
            try:
                html = response.content.decode("gb2312")
            except UnicodeDecodeError:
                print("gb18030")
                html = response.content.decode("gb18030")
            doc = pq(html)
            print(doc("#frmIndex > script").text())
            print(doc("#TblGwycj > tbody > tr:nth-child(5) > td:nth-child(2)").text())
            print(doc("#TblGwycj > tbody > tr:nth-child(7) > td:nth-child(2)").text())
    except ConnectTimeout:
        print("time out")

def test():
    url="http://httpbin.org/post"
    data = {
        "TxtName": "洪维",
        "TxtHaoMa": "10224133302",
        "txtJym": "1234",
        "__VIEWSTATE": "/wEPDwUKMTAwMzgzOTg0Ng9kFgICAw9kFgICAQ9kFgQCAQ9kFgYCAQ8PFgIeBFRleHQFYjIwMjDpqp7no4vlkLnlrrjngrXmuLfpjY/uhIDlp5/pjZvmqYjntJnmtZzng5jnmq/nkoDvuYDnmYLplJvlpIvlq5HopLDmm6Dnkarnkofmm5/lnprnvIHilYLluJPpjZo/ZGQCBw8PFgIfAAUP5YeG6ICD6K+B5Y+377yaZGQCEQ8PZBYCHgdvbmNsaWNrBRpKYXZhc2NyaXB0OnJldHVybiBjaGVjaygpO2QCAw8PFgIeB1Zpc2libGVoZBYGAgEPDxYCHwAFYjIwMjDpqp7no4vlkLnlrrjngrXmuLfpjY/uhIDlp5/pjZvmqYjntJnmtZzng5jnmq/nkoDvuYDnmYLplJvlpIvlq5HopLDmm6Dnkarnkofmm5/lnprnvIHilYLluJPpjZo/ZGQCAw88KwARAgAPFgIfAmhkDBQrAABkAgUPDxYCHwJnZGQYAQUJR3JpZFZpZXcxD2dkP1+WXklNZrMI8Kgk4na4JgqAwxIjVd4qKF1ZOwfrVHA=",
        "__VIEWSTATEGENERATOR": "AA59DA6E",
        "__EVENTVALIDATION": "/wEdAAWzKB3ewsjUs+nC6x7ILKlJvqpQkv2FJlCd366NAvz8uR/0J+7A+X+rVovkFDt+4BZKZ5fmGEq5xI7G200hjm3wPOaW1pQztoQA36D1w/+bXd8b5jE3/iVt8vZwb3N4VrxzJu0SwQeH5Xt79JuP8qZ1",
        "btnSubmit": "查　询",
    }
    response = rq.post(url,data=data,headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 Edg/85.0.564.63'

        })
    open("re.html", "wb").write(response.content)

u = URLObject(url)
# print(rq.utils.quote("洪维", encoding='gbk'))
test()
# get(u.relative(image_url), u.relative(action))
