from datetime import datetime

from sqlalchemy.sql import text

from app import db
from app.lib.cms_lib.str_util import StrUtil


class CmsOperationLog(db.Model):
    __tablename__ = 'CMS_OPERATION_LOG'

    operation_date = db.Column(db.DateTime, primary_key=True)
    operation_cd = db.Column(db.String(40), primary_key=True, index=True)
    user_info_id = db.Column(db.Integer)
    db_id = db.Column(db.Integer)
    object_id = db.Column(db.Integer)
    object_type = db.Column(db.String(20))
    ip_addr = db.Column(db.String(30))
    note = db.Column(db.String(2000))

    def __init__(self, user_id=None, db_id=None):
        self.user_info_id = user_id
        self.db_id = db_id

    def addOperationLog(self, cmsOperationLog, operation_cd, object_id='', object_type='', note=''):
        cmsOperationLog.operation_date = datetime.now()
        cmsOperationLog.operation_cd = operation_cd
        cmsOperationLog.object_id = object_id
        cmsOperationLog.object_type = object_type
        cmsOperationLog.ip_addr = StrUtil.get_ip_addr()
        cmsOperationLog.note = note
        return db.session.add(cmsOperationLog)

    # Daily Log検索処理
    def getCmsDailyLogList(self, form):
        selectSql = '''
            SELECT TO_CHAR(T.OPERATION_DATE, 'YYYY/MM/DD') OPERATION_DATE,
                   TO_CHAR(T.OPERATION_DATE, 'HH24:MI:SS') TIME,
                   T.OPERATION_CD, T.COMPANY_NAME_JP, T.DEPT_NAME_JP, T.USER_NAME_JP,
                   T.NOTE, T.IP_ADDR
              FROM CMS_OPERATION_LOG_VIEW T
             WHERE T.DB_ID = :db_id
               {where_sql}
             ORDER BY T.OPERATION_DATE
        '''
        params = {}
        params['db_id'] = form["db_id"]
        where_sql = ''
        if form["log_date1"] is not None and form["log_date1"]:
            where_sql += "AND TO_CHAR(OPERATION_DATE, 'YYYY-MM-DD') >= :ops_date_from "
            params['ops_date_from'] = form["log_date1"]
        if form["log_date2"] is not None and form["log_date2"]:
            where_sql += "AND TO_CHAR(OPERATION_DATE, 'YYYY-MM-DD') <= :ops_date_to "
            params['ops_date_to'] = form["log_date2"]

        selectSql = selectSql.format(where_sql=where_sql)
        rst = db.session.execute(text(selectSql), params)
        return rst
