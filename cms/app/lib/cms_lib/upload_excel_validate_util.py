import numpy as np
import pandas as pd
from flask_login import current_user
from numpy import nan

from app import db
from app.controllers.package import PkgCmsLog
from app.lib.cms_lib.str_util import StrUtil
from app.lib.conf.const import Const
from app.models.cms_common import CmsCommon
from app.models.cms_admin.cms_keyword_master import CmsKeywordMaster
from app.models.cms_admin.cms_keyword_setting import CmsKeywordSetting
from app.models.cms.cms_object import CmsObject
from app.models.cms.cms_object_keyword import CmsObjectKeyword
from app.models.cms_db_admin.cms_object_prop_selection_list import CmsObjectPropSelectionList
from app.models.cms_db_admin.cms_object_prop_selection_mst import CmsObjectPropSelectionMst
from app.services.cms.property_service import format_object_log_note


class UploadExcelValidateUtil:

    @staticmethod
    def read_sql(sql):
        resp = db.session.execute(sql)
        return pd.DataFrame(resp.fetchall(), None, resp.keys())

    def __init__(self, excel_filename, db_id, obj_type_id):
        self.excel_filename = excel_filename
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
        excel_pd = pd.read_excel(self.excel_filename, skiprows=[0, 2], dtype=str, engine="openpyxl")
        # 空行を削除する
        self.excel_pd = excel_pd.loc[~excel_pd.isna().all(1)].fillna("")
        # エンプティexcelの場合は直ぐに戻る
        if self.excel_pd.empty:
            self.errors.extend(["File is empty."])
            return False
        self.excel_pd.index += 4

        # htmlに表示される列ヘッダー
        self.headers = ["Excel Idx"] + self.excel_pd.columns.to_list()
        # 以下はチェックために使うSQLのデータ
        self.obj_property_pd = self.read_sql(
            f"SELECT * FROM CMS_OBJECT_PROPERTY WHERE OBJECT_TYPE_ID = {self.obj_type_id}").drop_duplicates(
            "property_name").set_index("property_name", False)

        # 先ずは列ヘッダーをチェック、不具合になったらFalseを戻る
        if not self.validate_headers(skip_null_check):
            return False
        smi_sub = db.session.query(CmsObjectPropSelectionMst.selection_mst_id).filter(
            CmsObjectPropSelectionMst.db_id == self.db_id).subquery()
        self.selection_name_list = list(
            map(lambda item: item[0], db.session.query(CmsObjectPropSelectionList.selection_name).filter(
                CmsObjectPropSelectionList.selection_mst_id == smi_sub.c.selection_mst_id).all()))
        self.multi_set_flg, keyword_mst_id = \
            db.session.query(CmsKeywordSetting.multi_set_flg, CmsKeywordSetting.keyword_mst_id).filter(
                CmsKeywordSetting.db_id == self.db_id).first()
        self.keyword_list = list(map(lambda item: item[0], db.session.query(CmsKeywordMaster.keyword).filter(
            CmsKeywordMaster.keyword_mst_id == keyword_mst_id).all()))
        self.folder_pd = self.read_sql(
            f"SELECT FOLDER_ID, PARENT_FOLDER_ID, FOLDER_NAME, CHILD_OBJECT_TYPE_ID FROM CMS_FOLDER WHERE DB_ID = {self.db_id} AND IS_DELETED = 0").drop_duplicates(
            "folder_name").set_index("folder_name", False)

        # データのチェック
        # チェックメッセージのDataFrame
        self.data_tips_pd = pd.DataFrame().reindex_like(self.excel_pd).fillna(False)
        self.excel_pd.apply(self.validate_data)

        # add error to errors
        self.data_tips_pd.apply(self.add_error)
        return (self.data_tips_pd == False).all(axis=None)

    def validate_headers(self, skip_null_check):
        valid_flag = True
        # 今の列ヘッダー
        columns = self.excel_pd.columns.to_series()
        # 不具合な列ヘッダーのチェック
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

    def validate_data(self, col):
        # 必須項目のチェック
        suffix = "%s({0}) " % col.name
        if col.name in self.exits_required_header:
            invalid_msg = "%s is required.(Excel Row No: {0})" % col.name
            condition = col.str.strip() != ""
            self.data_tips_pd[col.name].where(condition, col.index.to_series().map(invalid_msg.format), True)
        # FOLDERのチェック
        if col.name == "FOLDER NAME":
            respond_pd = col.str.split("->", expand=True).stack(dropna=True).str.strip().reset_index(
                name="folder_name").rename(
                columns={"level_0": "index", "level_1": "list_index"}).merge(
                self.folder_pd.reset_index(drop=True), "left", "folder_name").set_index("index", False)
            last_ele_pd = respond_pd.groupby(respond_pd.index).agg("last")
            invalid_type = last_ele_pd[
                (last_ele_pd.child_object_type_id != int(self.obj_type_id)) & (
                    last_ele_pd.folder_id.notna())]
            invalid_folder = respond_pd[
                (respond_pd.folder_name != "") & (respond_pd.folder_id.isna())].drop_duplicates("index")
            group_by_pd = respond_pd.groupby(respond_pd.index).agg(
                {"folder_id": lambda x: np.sum(x.to_list()) - x.iat[-1],
                 "parent_folder_id": lambda x: np.sum(x.to_list()) - x.iat[0]})
            invalid_order_index = group_by_pd[(group_by_pd['folder_id'] != group_by_pd["parent_folder_id"]) & (
                group_by_pd['folder_id'].notna())].index
            if not invalid_type.empty:
                self.data_tips_pd.loc[invalid_type.index, col.name] = invalid_type["folder_name"].map(
                    (suffix + "is invalid folder for this object type.").format) + invalid_type.index.map(
                    "(Excel Row No: {0})".format)
            if not invalid_folder.empty:
                self.data_tips_pd.loc[invalid_folder["index"], col.name] = invalid_folder["folder_name"].map(
                    (suffix + "is invalid folder name.").format) + invalid_folder["index"].map(
                    "(Excel Row No: {0})".format)
            if not invalid_order_index.empty:
                self.data_tips_pd.loc[invalid_order_index, col.name] = col[invalid_order_index].map(
                    (suffix + "is invalid data.").format) + invalid_order_index.to_series().map(
                    "(Excel Row No: {0})".format)
        else:
            condition = None
            property_type = self.obj_property_pd.at[col.name, "property_type"]
            # TEXT型のチェック
            if property_type == "TEXT":
                invalid_msg = suffix + "is too long."
                validate_rule, validate_err_msg = self.obj_property_pd.loc[
                    col.name, ["validate_rule", "validate_err_msg"]]
                if validate_rule and validate_err_msg:
                    validate_err_msg = validate_err_msg.replace("<#DATA#>", "{0}")
                    self.data_tips_pd[col.name].where(col.str.match(validate_rule) | (col == ""),
                                                      col.map(validate_err_msg.format) + col.index.to_series().map(
                                                          "(Excel Row No: {0})".format), True)
                data_size = self.obj_property_pd.at[col.name, "data_size"]
                condition = col.map(StrUtil.lenb) < (data_size or float("inf"))
            # NUMBER型のチェック
            elif property_type == "NUMBER":
                invalid_number_msg = suffix + "is invalid number."
                too_large_msg = suffix + "is too large."
                i_len, f_len = self.obj_property_pd.loc[col.name, ["i_len", "f_len"]]
                i_len, f_len = i_len or float("inf"), f_len or float("inf")
                tem_pd = col.str.extract("^([0-9]+)(\.([0-9]+))?$").apply(lambda row: row.str.len()).fillna(0)
                tem_pd["ilen"] = tem_pd[0] + tem_pd[2]
                invalid_number = (tem_pd["ilen"] == 0) & (col != "")
                too_large = (col != "") & (tem_pd["ilen"] != 0) & ((tem_pd["ilen"] > i_len) | (tem_pd[2] > f_len))
                self.data_tips_pd[col.name].mask(invalid_number,
                                                 col.map(invalid_number_msg.format) + col.index.to_series().map(
                                                     "(Excel Row No: {0})".format), True)
                self.data_tips_pd[col.name].mask(too_large, col.map(too_large_msg.format) + col.index.to_series().map(
                    "(Excel Row No: {0})".format), True)
            # DATE型のチェック
            elif property_type == "DATE":
                invalid_msg = suffix + "is invalid date format."
                date_col = pd.to_datetime(col, errors="coerce", format="%Y-%m-%d %H:%M:%S")
                condition = date_col.notna()
            # SELECT型のチェック
            elif property_type == "SELECT":
                invalid_msg = suffix + "is invalid data."
                condition = col.isin(self.selection_name_list)
            # KEYWORD型のチェック
            elif property_type == "KEYWORD":
                invalid_msg = suffix + "is invalid data."
                condition = col.isin(self.keyword_list) if not self.multi_set_flg else col.str.split(",").apply(
                    lambda l: pd.Series(l).str.strip().isin(self.keyword_list).all())
            # ブランクは必須項目のチェックをするので、ここはチェックしない
            if condition is not None:
                condition |= (col == "")
                self.data_tips_pd[col.name].where(condition, col.map(invalid_msg.format) + col.index.to_series().map(
                    "(Excel Row No: {0})".format), True)

    def add_error(self, row):
        self.errors.extend(row[row != False])

    def save_to_db(self, log_notes_format):
        excel_pd = pd.read_excel(self.excel_filename, skiprows=[0, 2], engine="openpyxl", dtype=str)
        # 空行を削除する
        excel_pd = excel_pd.loc[~excel_pd.isna().all(1)]
        rowCount = len(excel_pd)
        folder_pd = self.read_sql(
            f"SELECT FOLDER_ID,PARENT_FOLDER_ID,FOLDER_NAME,CHILD_OBJECT_TYPE_ID FROM CMS_FOLDER WHERE DB_ID = {self.db_id} AND IS_DELETED = 0")
        obj_property_pd = self.read_sql(
            f"SELECT PROPERTY_NAME,DB_COLUMN_NAME,PROPERTY_TYPE FROM CMS_OBJECT_PROPERTY WHERE OBJECT_TYPE_ID = {self.obj_type_id}").append(
            {"property_name": "FOLDER NAME", "db_column_name": "folder_name"}, True).drop_duplicates("property_name")
        selection_list_pd = self.read_sql(
            f'''SELECT SELECTION_ID, SELECTION_NAME FROM CMS_OBJECT_PROP_SELECTION_LIST
                WHERE SELECTION_MST_ID in (
                   SELECT SELECTION_MST_ID FROM CMS_OBJECT_PROP_SELECTION_MST
                   WHERE DB_ID = {self.db_id})''')
        keyword_list_pd = self.read_sql(
            f'''SELECT KEYWORD_ID,KEYWORD FROM CMS_KEYWORD_MASTER 
                WHERE KEYWORD_MST_ID in (
                    SELECT KEYWORD_MST_ID FROM CMS_KEYWORD_SETTING
		            WHERE DB_ID = {self.db_id})'''
        )

        # [番号   IDX_TEXT_001    TEXT] このようなMAP
        prop_column_mapping_pd = pd.DataFrame(excel_pd.columns.to_list(), columns=["property_name"]).merge(
            obj_property_pd, "left", "property_name").set_index("db_column_name", False)
        # columnsはDBの列名前を取り替え
        excel_pd.columns = prop_column_mapping_pd.db_column_name = prop_column_mapping_pd.db_column_name.str.lower()
        excel_pd["object_type_id"] = int(self.obj_type_id)
        excel_pd["db_id"] = int(self.db_id)
        excel_pd["object_id"] = CmsCommon.getObjectIdSeqList(rowCount)

        # --debug用object_id取得メソッド
        # excel_pd["object_id"] = range(25700, 25700 + rowCount)
        # folder_idの列をつけます
        excel_pd["parent_folder_id"] = excel_pd["folder_name"].str.split("->").apply(lambda l: l[-1].strip()).replace(
            folder_pd["folder_name"].to_list(), folder_pd["folder_id"].to_list()
        )
        type_groupby = prop_column_mapping_pd.groupby("property_type")

        for type_name, group in type_groupby:
            names = group.db_column_name
            if type_name == "SELECT":
                # select型の列にselection_nameをselection_mst_idに換える
                excel_pd[names] = excel_pd[names].replace(selection_list_pd["selection_name"].to_list(),
                                                          selection_list_pd["selection_id"].to_list())
            elif type_name == "NUMBER":
                excel_pd[names] = excel_pd[names].astype(np.float64)
            elif type_name == "DATE":
                excel_pd[names] = excel_pd[names].astype(np.datetime64)
            elif type_name == "KEYWORD":
                # keyword型を保存するために使う結構を作成,列は以下のようです
                # object_id　 db_columns_name 　keyword_id
                keyword_save_pd = excel_pd[names].rename(str.upper, axis=1).stack()
                if not keyword_save_pd.empty:
                    keyword_save_pd = keyword_save_pd.str.split(",", expand=True).stack(
                        dropna=True).str.strip().reset_index("db_column_name").reset_index(1, True).rename(
                        columns={0: "keyword_id"}).replace(
                        keyword_list_pd["keyword"].to_list(), keyword_list_pd["keyword_id"].to_list()).combine_first(
                        excel_pd[["object_id"]]).drop_duplicates()
                    # keyword型を保存する
                    db.session.execute(CmsObjectKeyword.__table__.insert(), keyword_save_pd.to_dict("records"))

        # 保存する
        excel_data = excel_pd.replace({nan: None}).to_dict("records")
        db.session.execute(CmsObject.__table__.insert(), excel_data)

        # オブジェクトの新規登録を記録する
        pkgCmsLog = PkgCmsLog()
        for index, obj_id in excel_pd["object_id"].iteritems():
            pkgCmsLog.saveOperationLog(
                current_user.tuid,
                self.db_id,
                operation_cd=Const.OPERATION_CD_CREATE_OBJECT,
                object_id=obj_id,
                object_type='OBJECT',
                note=format_object_log_note(excel_pd.loc[index], log_notes_format)
            )

        db.session.commit()
        return rowCount
