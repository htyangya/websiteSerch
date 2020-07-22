import re
import sys
from datetime import datetime

from flask_login import current_user
from sqlalchemy import Sequence
from sqlalchemy.sql import text

from app import db
from app.lib.cms_lib.str_util import StrUtil
from app.lib.conf.const import Const
from app.models.cms_object_property import CmsObjectProperty


class CmsObject(db.Model):
    __tablename__ = 'CMS_OBJECT'
    id_seq = Sequence('OBJECT_ID_SEQUENCE')
    object_id = db.Column(db.Numeric(10), id_seq,
                          server_default=id_seq.next_value(), primary_key=True)
    parent_folder_id = db.Column(db.Numeric(10))
    db_id = db.Column(db.Numeric(10))
    object_type_id = db.Column(db.Numeric(10))
    idx_text_001 = db.Column(db.String(500))
    idx_text_002 = db.Column(db.String(500))
    idx_text_003 = db.Column(db.String(500))
    text_001 = db.Column(db.String(2000))
    text_002 = db.Column(db.String(2000))
    text_003 = db.Column(db.String(2000))
    text_004 = db.Column(db.String(2000))
    text_005 = db.Column(db.String(2000))
    text_006 = db.Column(db.String(2000))
    text_007 = db.Column(db.String(2000))
    text_008 = db.Column(db.String(2000))
    text_009 = db.Column(db.String(2000))
    text_010 = db.Column(db.String(2000))
    text_011 = db.Column(db.String(2000))
    text_012 = db.Column(db.String(2000))
    text_013 = db.Column(db.String(2000))
    text_014 = db.Column(db.String(2000))
    text_015 = db.Column(db.String(2000))
    text_016 = db.Column(db.String(2000))
    text_017 = db.Column(db.String(2000))
    text_018 = db.Column(db.String(2000))
    text_019 = db.Column(db.String(2000))
    text_020 = db.Column(db.String(2000))
    text_021 = db.Column(db.String(2000))
    text_022 = db.Column(db.String(2000))
    text_023 = db.Column(db.String(2000))
    text_024 = db.Column(db.String(2000))
    text_025 = db.Column(db.String(2000))
    text_026 = db.Column(db.String(2000))
    text_027 = db.Column(db.String(2000))
    text_028 = db.Column(db.String(2000))
    text_029 = db.Column(db.String(2000))
    text_030 = db.Column(db.String(2000))
    num_001 = db.Column(db.Numeric())
    num_002 = db.Column(db.Numeric())
    num_003 = db.Column(db.Numeric())
    num_004 = db.Column(db.Numeric())
    num_005 = db.Column(db.Numeric())
    num_006 = db.Column(db.Numeric())
    num_007 = db.Column(db.Numeric())
    num_008 = db.Column(db.Numeric())
    num_009 = db.Column(db.Numeric())
    num_010 = db.Column(db.Numeric())
    num_011 = db.Column(db.Numeric())
    num_012 = db.Column(db.Numeric())
    num_013 = db.Column(db.Numeric())
    num_014 = db.Column(db.Numeric())
    num_015 = db.Column(db.Numeric())
    num_016 = db.Column(db.Numeric())
    num_017 = db.Column(db.Numeric())
    num_018 = db.Column(db.Numeric())
    num_019 = db.Column(db.Numeric())
    num_020 = db.Column(db.Numeric())
    num_021 = db.Column(db.Numeric())
    num_022 = db.Column(db.Numeric())
    num_023 = db.Column(db.Numeric())
    num_024 = db.Column(db.Numeric())
    num_025 = db.Column(db.Numeric())
    num_026 = db.Column(db.Numeric())
    num_027 = db.Column(db.Numeric())
    num_028 = db.Column(db.Numeric())
    num_029 = db.Column(db.Numeric())
    num_030 = db.Column(db.Numeric())
    date_001 = db.Column(db.DateTime)
    date_002 = db.Column(db.DateTime)
    date_003 = db.Column(db.DateTime)
    date_004 = db.Column(db.DateTime)
    date_005 = db.Column(db.DateTime)
    date_006 = db.Column(db.DateTime)
    date_007 = db.Column(db.DateTime)
    date_008 = db.Column(db.DateTime)
    date_009 = db.Column(db.DateTime)
    date_010 = db.Column(db.DateTime)
    is_deleted = db.Column(db.Numeric(1), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(10), default=lambda: current_user.get_id())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.String(10), default=lambda: current_user.get_id())
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.String(10))
    ctx_indexed_flg = db.Column(db.Numeric(1), default=0)

    def __init__(self, db_id=None, object_id=None):
        self.db_id = db_id
        self.object_id = object_id

    def getCmsObject(self, object_id):
        return db.session.query(CmsObject).filter(CmsObject.object_id == object_id, CmsObject.is_deleted == 0).first()

    def addObject(self, cmsObject, userId):
        cmsObject.is_deleted = 0
        cmsObject.ctx_indexed_flg = 0
        cmsObject.created_by = userId
        cmsObject.created_at = datetime.now()
        cmsObject.updated_by = userId
        cmsObject.updated_at = datetime.now()
        return db.session.add(cmsObject)

    def ctxUpdObject(self, object_id, ctx_indexed_flg):
        updObject = db.session.query(CmsObject).filter(CmsObject.object_id == object_id,
                                                       CmsObject.is_deleted == 0).first()
        updObject.ctx_indexed_flg = ctx_indexed_flg

    def delObject(self, object_id, userId):
        delObject = db.session.query(CmsObject).filter(CmsObject.object_id == object_id).first()
        delObject.is_deleted = 1
        delObject.deleted_at = datetime.now()
        delObject.deleted_by = userId

    # オブジェクトリストを取得
    def getCtxObjectList(self, db_id, row_num):
        if not row_num:
            where_sql = ''
        else:
            where_sql = 'AND ROWNUM <= ' + row_num

        selectSql = '''
            SELECT O.OBJECT_TYPE_ID, O.OBJECT_ID, O.PARENT_FOLDER_ID, O.UPDATED_AT, OT.CTX_TITLE_FORMAT
            FROM CMS_OBJECT O, CMS_OBJECT_TYPE OT
            WHERE O.OBJECT_TYPE_ID = OT.OBJECT_TYPE_ID
            AND O.IS_DELETED = 0
            AND O.CTX_INDEXED_FLG = 0
            AND O.DB_ID = :db_id
            AND OT.CTX_FLG = 1
            {where_sql}
            ORDER BY O.UPDATED_AT DESC
        '''

        selectSql = selectSql.format(where_sql=where_sql)
        t = text(selectSql)
        rst = db.session.execute(t, {'db_id': db_id})
        return rst

    # タイトルテキストを取得
    def getCtxTitle(self, object_type_id, object_id, file_id, ctx_title_format, ctx_title_rst):
        ctx_text_arr = []
        try:
            index = 0
            object_column_sql = ''
            file_column_sql = ''
            from_addition_sql = ''
            and_addition_sql = ''

            ctx_title_format_arr = re.findall(r'[A-Za-z_0-9]+', ctx_title_format)
            for _ctx_title_format in ctx_title_format_arr:
                if index > 0:
                    if file_id is not None and _ctx_title_format in 'FILE_NAME':
                        file_column_sql += ', '
                    else:
                        object_column_sql += ', '

                if file_id is not None and _ctx_title_format in 'FILE_NAME':
                    file_column_sql += 'F.{} COL_{}'.format(_ctx_title_format, index)
                    from_addition_sql = ', CMS_FILE F'
                    and_addition_sql = 'AND O.OBJECT_ID = F.PARENT_OBJECT_ID'
                    and_addition_sql = Const.CONTACT_FORMAT.format(and_addition_sql,
                                                                   'AND F.FILE_ID = {}'.format(file_id))
                    and_addition_sql = Const.CONTACT_FORMAT.format(and_addition_sql, 'AND F.IS_DELETED = 0')
                else:
                    object_column_sql += 'O.{} COL_{}'.format(_ctx_title_format, index)
                index += 1

            selectSql = '''
                SELECT {object_column_sql} {file_column_sql}
                FROM CMS_OBJECT O {from_addition_sql}
                WHERE O.IS_DELETED = 0
                AND O.OBJECT_ID = :object_id
                {and_addition_sql}
            '''

            selectSql = selectSql.format(object_column_sql=object_column_sql,
                                         file_column_sql=file_column_sql,
                                         from_addition_sql=from_addition_sql,
                                         and_addition_sql=and_addition_sql)
            t = text(selectSql)
            rst = db.session.execute(t, {'object_id': object_id}).first()

            if rst is not None:
                for idx in range(0, index):
                    # StrUtil.print_debug('rst idx:[{}]'.format(str(rst.items()[idx][1])))
                    # ctx_text_arr.append(StrUtil.get_safe_string(rst.items()[idx][1]))
                    ctx_title_format = ctx_title_format.replace('<#' + ctx_title_format_arr[idx] + '#>',
                                                                StrUtil.get_safe_string(rst.items()[idx][1]))

            # 全文検索の対象にするテキストはcms_object_property.ctx_flg = 1で設定されている属性にする
            if object_type_id:
                index = 0
                object_column_sql = ''
                cmsObjectProperty = CmsObjectProperty()
                for ctx_db_obj in cmsObjectProperty.getCtxObjectDbNames(object_type_id):
                    if index > 0:
                        object_column_sql += ', '
                    object_column_sql += 'O.{} COL_{}'.format(ctx_db_obj.db_column_name, index)
                    index += 1

                selectSql = '''
                    SELECT {object_column_sql}
                    FROM CMS_OBJECT O
                    WHERE O.IS_DELETED = 0
                    AND O.OBJECT_ID = :object_id
                '''

                selectSql = selectSql.format(object_column_sql=object_column_sql)
                t = text(selectSql)
                rst = db.session.execute(t, {'object_id': object_id}).first()

                if rst is not None:
                    for idx in range(0, index):
                        ctx_text_val = StrUtil.get_safe_string(rst.items()[idx][1])
                        if ctx_text_val:
                            ctx_text_arr.append(ctx_text_val)

        except Exception as e:
            db.session.rollback()
            tb = sys.exc_info()[2]
            StrUtil.print_error("getCtxTitle info:{} error_msg:{}".format(
                'object_id:{} file_id:{} ctx_title_format:{}'.format(
                    object_id, file_id, ctx_title_format
                ),
                str(e.with_traceback(tb)))
            )
            ctx_title_rst['CTX_TITLE'] = ctx_title_format
            ctx_title_rst['CTX_TEXT'] = "\n".join(ctx_text_arr)
            ctx_title_rst['CTX_ERROR_FLG'] = 1
            ctx_title_rst['CTX_ERROR_LOG'] = str(e.with_traceback(tb))
            return

        ctx_title_rst['CTX_TITLE'] = ctx_title_format
        ctx_title_rst['CTX_TEXT'] = "\n".join(ctx_text_arr)
        ctx_title_rst['CTX_ERROR_FLG'] = 0
        ctx_title_rst['CTX_ERROR_LOG'] = ''

    # フォルダタブのオブジェクトリストを取得
    def getObjectListInfo(self, folder_id, colList, sortColList):
        selectSql = '''
            SELECT O.OBJECT_ID,
                   TO_CHAR(O.UPDATED_AT, 'YYYY/MM/DD hh24:mi:ss') UPDATED_AT_STR,
                   O.UPDATED_BY
                   {column_sql}
            FROM CMS_OBJECT O
            WHERE O.IS_DELETED = 0
              AND O.PARENT_FOLDER_ID = :folder_id
            {sort_sql}
        '''
        cmsObject = CmsObject()
        column_sql = cmsObject.getColumnSql(colList)
        sort_sql = cmsObject.getSortColumnSql(sortColList)

        selectSql = selectSql.format(column_sql=column_sql, sort_sql=sort_sql)
        t = text(selectSql)
        rst = db.session.execute(t, {'folder_id': folder_id})
        return cmsObject.getResultList(rst)

    # フォルダタブのオブジェクトリストを取得
    def searchObjectList(self, condList, colList, sortColList):
        selectSql = '''
            SELECT O.OBJECT_ID,
                   TO_CHAR(O.UPDATED_AT, 'YYYY/MM/DD hh24:mi:ss') UPDATED_AT_STR,
                   O.UPDATED_BY,
                   O.PARENT_FOLDER_ID
                   {column_sql}
            FROM CMS_OBJECT O
            WHERE O.IS_DELETED = 0
            {condition_sql}
            {sort_sql}
        '''
        cmsObject = CmsObject()
        column_sql = cmsObject.getColumnSql(colList)
        sort_sql = cmsObject.getSortColumnSql(sortColList)
        condition_sql = ""
        for cond in condList:
            condition_sql += cond

        selectSql = selectSql.format(column_sql=column_sql, condition_sql=condition_sql, sort_sql=sort_sql)
        t = text(selectSql)
        rst = db.session.execute(t, {})
        return cmsObject.getResultList(rst)

    # キーワードタブのオブジェクトリストを取得
    def getObjectListKeyword(self, object_id_list, colList, sortColList):
        selectSql = '''
            SELECT O.OBJECT_ID,
                   O.PARENT_FOLDER_ID,
                   TO_CHAR(O.UPDATED_AT, 'YYYY/MM/DD hh24:mi:ss') UPDATED_AT_STR,
                   O.UPDATED_BY
                   {column_sql}
            FROM CMS_OBJECT O
            WHERE O.IS_DELETED = 0
              AND O.OBJECT_ID IN ({in_sql})
            {sort_sql}
        '''
        in_sql = ','.join(map(str, object_id_list))
        cmsObject = CmsObject()
        column_sql = cmsObject.getColumnSql(colList)
        sort_sql = cmsObject.getSortColumnSql(sortColList)

        selectSql = selectSql.format(column_sql=column_sql, in_sql=in_sql, sort_sql=sort_sql)
        t = text(selectSql)

        rst = db.session.execute(t, {})
        return cmsObject.getResultList(rst)

    # Property画面表示カラムを取得する
    def getPropertyObjectValues(self, object_id, colList):
        selectSql = '''
            SELECT O.OBJECT_ID, O.OBJECT_TYPE_ID {column_sql}
            FROM CMS_OBJECT O
            WHERE O.IS_DELETED = 0
              AND O.OBJECT_ID = :object_id
        '''
        column_sql = self.getColumnSql(colList)
        selectSql = selectSql.format(column_sql=column_sql)
        t = text(selectSql)
        rst = db.session.execute(
            t,
            {'object_id': object_id}).first()
        dic = {}
        if rst is not None:
            for column, val in rst.items():
                if val is None:
                    val = ""
                dic = {**dic, **{column: val}}
        return dic

    def getColumnSql(self, colList):
        index = 0
        column_sql = ""
        for col in colList:
            if "SELECT" == col.get("property_type"):
                column_sql += ",O." + col.get("db_column_name") + " COL_" + str(index)
                column_sql += ",(SELECT S.SELECTION_NAME FROM CMS_OBJECT_PROP_SELECTION_LIST S WHERE S.SELECTION_MST_ID" \
                              " = " + str(col.get("selection_mst_id")) + " AND S.SELECTION_ID = O." \
                              + col.get("db_column_name") + " ) COL_" + str(index) + "_LABEL"
            elif "KEYWORD" == col.get("property_type"):
                column_sql += ",PKG_CMS_SEARCH_UTIL.GET_OBJECT_KEYWORD_TEXT(O.OBJECT_ID, '" + col.get(
                    "db_column_name") + "') COL_" + str(index)
                column_sql += ",PKG_CMS_SEARCH_UTIL.GET_OBJECT_KEYWORD_ID_TEXT(O.OBJECT_ID, '" + col.get(
                    "db_column_name") + "') KEYWORD_ID_TEXT_" + str(index)
            else:
                column_sql += ",O." + col.get("db_column_name") + " COL_" + str(index)

            if "FILE" == col.get("link_type") and col.get("link_type_id") is not None:
                column_sql += ",(SELECT MAX(F.FILE_ID) FROM CMS_FILE F WHERE F.IS_DELETED = 0 AND F.PARENT_OBJECT_ID = " \
                              "O.OBJECT_ID AND F.FILE_TYPE_ID = " + str(col.get("link_type_id")) + ") FILE_ID_" + str(
                    index)
                column_sql += ",(SELECT COUNT(1) FROM CMS_FILE F WHERE F.IS_DELETED = 0 AND F.PARENT_OBJECT_ID = " \
                              "O.OBJECT_ID AND F.FILE_TYPE_ID = " + str(col.get("link_type_id")) + ") FILE_CNT_" + str(
                    index)

            if "URL" == col.get("link_type") and col.get("link_format") is not None:
                link_format_arr = re.findall('.*<#(.*)#>.*', col.get("link_format"))
                link_text_sql = ",'" + col.get("link_format") + "'"
                for link_format in link_format_arr:
                    link_col_sql = "'|| O." + link_format + " ||'"
                    link_text_sql = link_text_sql.replace("<#" + link_format + "#>", link_col_sql)

                column_sql += link_text_sql + " COL_" + str(index) + "_LABEL"
            index += 1

        return column_sql

    def getSortColumnSql(self, sortColList):
        sort_sql = ""
        index = 0
        if len(sortColList) > 0:
            sort_sql = "ORDER BY "
            for col in sortColList:
                if index > 0:
                    sort_sql += ", "
                if col.get("property_type") == "KEYWORD":
                    sort_sql += "to_char(" + col.get("db_column_name") + ") " + col.get("sort_key_order")
                else:
                    sort_sql += col.get("db_column_name") + " " + col.get("sort_key_order")
                index += 1

        return sort_sql

    def getResultList(self, rst):
        dic, array = {}, []
        for row_proxy in rst:
            for column, val in row_proxy.items():
                if val is None:
                    val = ""
                dic = {**dic, **{column: val}}
            array.append(dic)

        return array
