import os
import sys

from flask import current_app

from app.lib.cms_lib.str_util import StrUtil
from app.util.output.csv_output import CsvOutput
from app.util.xml_reader import XmlReader


class DailyLogCsvOutput(CsvOutput):

    def __init__(self):
        self.csvDir = "csv"
        self.headerFileName = 'DAILY_LOG_LIST.txt'
        self.xmlName = 'DailyLogOutputField.xml'
        self.xmlReader = None

    def _init_xml(self):
        xmlFilePath = os.path.join(current_app.root_path, self.csvDir, self.xmlName)
        self.xmlReader = XmlReader(xmlFilePath)
        self.xmlReader.read()

    # Csvファイルを作る
    def createCsvFile(self, writer):
        self._init_xml()

        try:
            # ヘッダを書き込み
            headerFilePath = os.path.join(current_app.root_path, self.csvDir, self.headerFileName)
            with open(headerFilePath, 'r', encoding='utf_8_sig') as f:
                l_strip = [s.strip() for s in f.readlines()]
                writer.writerow(l_strip)

            # データリストを書き込み
            if self.dataList is not None:
                for data in self.dataList:
                    rowData = []
                    for col in self.xmlReader.getColumnList():
                        if hasattr(data, col):
                            rowData.append(getattr(data, col))
                        else:
                            rowData.append('')
                    writer.writerow(rowData)

        except Exception as e:
            tb = sys.exc_info()[2]
            StrUtil.print_error("createCsvFile. error_msg:{}".format(str(e.with_traceback(tb))))
