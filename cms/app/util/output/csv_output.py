import csv
import os
from flask import current_app

from app.lib.cms_lib.date_util import DateUtil
from app.lib.cms_lib.str_util import StrUtil
from app.lib.conf.const import Const


class CsvOutput:

    def __init__(self, csvFileName=None):
        self.csvFileName = csvFileName
        self.csvFilePath = None
        self.csvTempDir = None
        self.headerData = None
        self.dataList = []

    def getCsvFileName(self):
        return self.csvFileName

    def setCsvFilePath(self, csvFilePath):
        self.csvFilePath = csvFilePath

    def setCsvTempDir(self, csvTempDir):
        self.csvTempDir = csvTempDir

    def setHeaderData(self, headerData):
        self.headerData = headerData

    def setDataList(self, dataList):
        self.dataList = dataList

    def execute(self):
        cds = DateUtil.current_date_str()
        tmp_path = os.path.join(self.csvTempDir, cds)
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path, exist_ok=True)

        tmp_file = os.path.join(tmp_path, (cds + Const.FILE_SUFFIX_CSV))
        with open(tmp_file, 'w', encoding='utf_8_sig', newline='') as f:
            writer = csv.writer(f)
            # Csvファイルを作る
            self.createCsvFile(writer)

        self.csvFileName = tmp_file
        return True

    # Csvファイルを作る
    def createCsvFile(self, writer):
        StrUtil.print_debug('createCsvFile')
