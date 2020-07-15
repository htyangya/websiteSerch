from datetime import datetime

from sqlalchemy.sql import text

from app import db


class CmsDb(db.Model):
    __tablename__ = 'CMS_DB'
    db_id = db.Column(db.Integer, primary_key=True)
    db_name = db.Column(db.String(100))
    session_cookie_name = db.Column(db.String(100))
    display_order = db.Column(db.Integer)
    login_message = db.Column(db.String(2000))
    information_message = db.Column(db.String(2000))
    remarks = db.Column(db.String(2000))
    is_deleted = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(32))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.String(32))
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.String(32))

    def __init__(self, db_id=None):
        self.db_id = db_id
        self.is_deleted = 0

    def __repr__(self):
        return '<Name %r>' % self.db_name

    def get_db_name(self):
        return self.db_name

    def get_login_message(self):
        return self.login_message

    def getCmsDb(db_id):
        return db.session.query(CmsDb).filter(CmsDb.db_id == db_id).first()

    def getCmsDbProperty(db_id):
        selectSql = '''
            SELECT T.DB_ID, T.DB_NAME, T.SESSION_COOKIE_NAME, T.DISPLAY_ORDER, 
                T.LOGIN_MESSAGE, T.INFORMATION_MESSAGE, T.REMARKS
            FROM CMS_DB T
            WHERE T.IS_DELETED = 0 AND T.DB_ID = :db_id
        '''
        t = text(selectSql)
        rst = db.session.execute(t, {'db_id': db_id}).first()

        dic = {}
        for column, val in rst.items():
            dic = {**dic, **{column: ('' if val is None else val)}}
        return dic

    def addDb(cmsDB, userId):
        cmsDB.is_deleted = 0
        cmsDB.created_by = userId
        cmsDB.created_at = datetime.now()
        cmsDB.updated_by = userId
        cmsDB.updated_at = datetime.now()
        return db.session.add(cmsDB)

    def delDb(db_id, userId):
        del_file = db.session.query(CmsDb).filter(CmsDb.db_id == db_id).first()
        del_file.is_deleted = 1
        del_file.deleted_at = datetime.now()
        del_file.deleted_by = userId

    def getCmsDbInfo(db_id):
        selectSql = '''
       SELECT T.DB_ID, T.DB_NAME, T.SESSION_COOKIE_NAME, T.DISPLAY_ORDER, 
            T.LOGIN_MESSAGE, T.INFORMATION_MESSAGE, T.REMARKS, T.IS_DELETED, T.CREATED_AT, 
            T.CREATED_BY, T.UPDATED_AT, T.UPDATED_BY, T.DELETED_AT, T.DELETED_BY
        FROM CMS_DB T
        WHERE T.IS_DELETED = 0 AND T.DB_ID = :db_id
        '''
        t = text(selectSql)
        rst = db.session.execute(t, {'db_id': db_id}).first()
        return rst

    @staticmethod
    def getCmsDbList():
        selectSql = '''
       SELECT T.DB_ID, T.DB_NAME, T.SESSION_COOKIE_NAME, T.DISPLAY_ORDER, 
            T.LOGIN_MESSAGE, T.INFORMATION_MESSAGE, T.REMARKS, T.IS_DELETED, T.CREATED_AT, 
            T.CREATED_BY, T.UPDATED_AT, T.UPDATED_BY
        FROM CMS_DB T
        WHERE T.IS_DELETED = 0
        ORDER BY T.DISPLAY_ORDER, T.DB_NAME
        '''
        rst = db.session.execute(text(selectSql), {})
        return rst
