import re
from io import BytesIO

import pytesseract
from PIL import Image
import requests as rq

from request_send import Search

url = "http://pta.guizhou.gov.cn/gwycj/GzCjcx/GzSearch.aspx?examSort=01&examDate=1&examName=2020%u9a9e%u78cb%u5439%u5bb8%u70b5%u6e37%u934f%ue100%u59df%u935b%u6a48%u7d19%u6d5c%u70d8%u76af%u7480%ufe40%u7642%u951b%u590b%u5ad1%u8930%u66e0%u746a%u7487%u66df%u579a%u7f01%u2542%u5e13%u935a%3f"

image_url = "http://pta.guizhou.gov.cn/gwycj/GzCjcx/gif.aspx"

search = Search(url, "贵州人事考试信息网策略1")
search.read_excel("成绩排名.xlsx")
search.start()
print(1)
# input("按任意键结束！")
