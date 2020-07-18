from collections import namedtuple

import pandas as pd
from app import db
from app.models.cms_keyword_master import CmsKeywordMaster
from app.models.cms_keyword_setting import CmsKeywordSetting
from app.models.cms_object_prop_selection_list import CmsObjectPropSelectionList


class UploadExcelValidateUtil:
    def __init__(self, excel_filename, db_id, obj_type_id):
        self.excel_filename = excel_filename
        self.db_id = db_id
        self.db_id = db_id
        self.obj_type_id = obj_type_id
        self.errors = []
        self.headers = None
        self.data_tips_pd = None
        self.excel_pd = None
        self.obj_property_pd = None
        self.selection_name_list = None
        self.multi_set_flg = None
        self.keyword_list = None
        self.folder_pd = None
        self.exits_required_header = None

    def validate(self, skip_null_check):
        # チェックされるexcel dataを用意
        self.excel_pd = pd.read_excel(self.excel_filename, skiprows=[0, 2], dtype=str).fillna("")
        # エンプティexcelの場合は直ぐに戻る
        if self.excel_pd.empty:
            return False
        self.excel_pd.index += 4
        # htmlに表示される列ヘーダー
        self.headers = ["Excel Idx"] + self.excel_pd.columns.to_list()
        # 以下はチェックために使うsqlのデータ
        self.obj_property_pd = pd.read_sql(
            f"SELECT * FROM CMS_OBJECT_PROPERTY WHERE OBJECT_TYPE_ID ={self.obj_type_id}",
            db.engine)
        # 先ずは列ヘーダーをチェック、不具合になったらfalseを戻る
        if not self.validate_headers(skip_null_check):
            return False
        self.selection_name_list = list(
            map(lambda item: item[0], db.session.query(CmsObjectPropSelectionList.selection_name).all()))
        self.multi_set_flg = db.session.query(CmsKeywordSetting.multi_set_flg).filter(
            CmsKeywordSetting.db_id == self.db_id).first()[0]
        self.keyword_list = list(map(lambda item: item[0], db.session.query(CmsKeywordMaster.keyword).all()))
        self.folder_pd = pd.read_sql(
            f"SELECT FOLDER_ID,PARENT_FOLDER_ID,FOLDER_NAME,CHILD_OBJECT_TYPE_ID FROM CMS_FOLDER WHERE DB_ID={self.db_id}",
            db.engine
        )
        # データのチェック
        # チェックメッセージのdataFrame
        self.data_tips_pd = pd.DataFrame().reindex_like(self.excel_pd).fillna(False)
        self.excel_pd.apply(self.check_data)
        # add error to errors
        self.data_tips_pd.apply(self.add_error)
        return (self.data_tips_pd == False).all(axis=None)

    def validate_headers(self, skip_null_check):
        valid_flag = True
        # 今の列ヘーダー
        columns = self.excel_pd.columns.to_series()
        # 不具合な列ヘーダーのチェック
        invalid_headers = columns[
            ~columns.isin(["FOLDER NAME"] + self.obj_property_pd["property_name"].to_list())]
        # 必須項目が存在しないのチェック
        required_header = pd.Series(["FOLDER NAME"])
        if not skip_null_check:
            opp = self.obj_property_pd
            required_header = opp[opp["nullable"] == "FALSE"]["property_name"].append(required_header,
                                                                                      ignore_index=True)
        # データをチェックために使うexits_required_headerを保存
        self.exits_required_header = columns[columns.isin(required_header)]
        not_exits_head = required_header[~required_header.isin(columns)]
        if not_exits_head.size:
            valid_flag = False
            self.errors.extend(map(lambda header: f"{header} is required.", not_exits_head))
        if invalid_headers.size:
            valid_flag = False
            self.errors.extend(map(lambda header: f"{header} is invalid property name.", invalid_headers))
        return valid_flag

    def check_data(self, col):
        # 必須項目のチェック
        if col.name in self.exits_required_header:
            invalid_msg = "%s is required.(Excel Row No: {0})" % col.name
            condition = col != ""
            self.data_tips_pd[col.name].where(condition, col.index.to_series().map(invalid_msg.format), True)
        # FOLDERのチェック
        if col.name == "FOLDER NAME":
            respond_pd = col.str.split("->").apply(self._check_folder)
            self.data_tips_pd[col.name].where(respond_pd["condition"] | (col == ""),
                                              respond_pd["msg"] + col.index.to_series().map(
                                                  "(Excel Row No: {0})".format), True)
        else:
            condition = None
            property_type = self.obj_property_pd.query("property_name==@col.name")["property_type"].iloc[0]
            # TEXT型のチェック
            if property_type == "TEXT":
                invalid_msg = "{0} is too long."
                data_size = self.obj_property_pd.query("property_name==@col.name")["data_size"].iloc[0]
                condition = col.str.len() < (data_size or float("inf"))
            # NUMBER型のチェック
            elif property_type == "NUMBER":
                invalid_msg = "{0} is invalid number."
                i_len, f_len = self.obj_property_pd.query("property_name==@col.name")[["i_len", "f_len"]].iloc[0]
                condition = col.str.extract("^(\d+)(\.(\d+))?$").apply(lambda row: row.str.len()).fillna(0).apply(
                    self._check_len, 1, args=(i_len or float("inf"), f_len or float("inf")))
            # DATE型のチェック
            elif property_type == "DATE":
                invalid_msg = "{0} is invalid date format."
                date_col = pd.to_datetime(col, errors="coerce", format="%Y-%m-%d %H:%M:%S")
                condition = date_col.notna() & col.str.match(r"\d{4}-\d{2}-\d{2}")
            # SELECT型のチェック
            elif property_type == "SELECT":
                invalid_msg = "{0} is invalid data."
                condition = col.isin(self.selection_name_list)
            # KEYWORD型のチェック
            elif property_type == "KEYWORD":
                invalid_msg = "{0} is invalid data."
                condition = col.isin(self.keyword_list) if not self.multi_set_flg else col.str.split(",").apply(
                    lambda l: pd.Series(l).isin(self.keyword_list).all())
            # ブランクは必須項目のチェックをする,ここでチェックしない
            if condition is not None:
                condition |= (col == "")
                self.data_tips_pd[col.name].where(condition, col.map(invalid_msg.format) + col.index.to_series().map(
                    "(Excel Row No: {0})".format), True)

    @staticmethod
    def _check_len(row, ilen, flen):
        re_ilen = row[0] + row[2]
        return re_ilen != 0 and re_ilen <= ilen and row[2] <= flen

    def _check_folder(self, folder_name_list):
        folder_list = []
        for i in range(len(folder_name_list) - 1, -1, -1):
            folder_name = folder_name_list[i]
            msg = "{0} is invalid folder name".format(folder_name)
            prop_pd = self.folder_pd.query("folder_name==@folder_name")[
                ["child_object_type_id", "folder_id", "parent_folder_id", ]]
            if prop_pd.empty:
                return pd.Series([False, msg], ["condition", "msg"])
            type_id, fid, pid = prop_pd.iloc[0]
            if type_id != int(self.obj_type_id):
                msg = "{0} is invalid folder for this object type".format(folder_name)
                return pd.Series([False, msg], ["condition", "msg"])
            folder_list.append((fid, pid))
        for i in range(len(folder_list) - 1):
            if folder_list[i][1] != folder_list[i + 1][0]:
                msg = "{0} is invalid folder name".format("->".join(folder_name_list))
                return pd.Series([False, msg], ["condition", "msg"])
        return pd.Series([True, msg], ["condition", "msg"])

    def add_error(self, row):
        self.errors.extend(row[row != False])
