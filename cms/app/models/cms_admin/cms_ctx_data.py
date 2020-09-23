from datetime import datetime

from sqlalchemy import text

from app import db


class CmsCtxData(db.Model):
    __tablename__ = 'CMS_CTX_DATA'
    db_id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer, primary_key=True)
    object_updated_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ctx_title = db.Column(db.String(32))
    ctx_text = db.Column(db.CLOB)
    ctx_error_log = db.Column(db.String(4000))
    data_type = db.Column(db.String(50))
    ctx_url = db.Column(db.String(300))
    ctx_error_flg = db.Column(db.Integer)

    def __init__(self, db_id=None, object_id=None):
        self.db_id = db_id
        self.object_id = object_id
        self.ctx_error_flg = 0

    def addCmsCtxData(self, cmsCtxData):
        cmsCtxData.object_updated_at = datetime.now()
        cmsCtxData.created_at = datetime.now()
        db.session.add(cmsCtxData)

    def delCmsCtxData(self, object_id, db_id):
        db.session.query(CmsCtxData).filter(CmsCtxData.object_id == object_id, CmsCtxData.db_id == int(db_id)).delete()

    def getCtxSearchListCnt(self, db_id, ctx_search_text):
        selectSql = '''
            SELECT COUNT(*) cnt
            FROM CMS_CTX_DATA D, CMS_OBJECT O
            WHERE CONTAINS(D.CTX_TEXT, '{ctx_search_text}', 1) > 0
            AND D.DB_ID = :db_id
            AND D.OBJECT_ID = O.OBJECT_ID
            AND O.IS_DELETED = 0
            AND D.CTX_ERROR_FLG = 0
            ORDER BY SCORE(1) DESC, D.CTX_TITLE
        '''

        selectSql = selectSql.format(ctx_search_text=ctx_search_text)

        exec_args = {'db_id': db_id}
        rst = db.session.execute(text(selectSql), exec_args).first()
        return rst.cnt

    def getCtxSearchList(self, db_id, ctx_search_text):
        selectSql = '''
            SELECT SCORE(1) SCORE_CNT, D.CTX_TITLE, D.OBJECT_ID, O.PARENT_FOLDER_ID FOLDER_ID,
                D.CTX_URL, TO_CHAR(D.OBJECT_UPDATED_AT, 'YYYY/MM/DD hh24:mi') OBJECT_UPDATED_AT
            FROM CMS_CTX_DATA D, CMS_OBJECT O
            WHERE CONTAINS(D.CTX_TEXT, '{ctx_search_text}', 1) > 0
            AND D.DB_ID = :db_id
            AND D.OBJECT_ID = O.OBJECT_ID
            AND O.IS_DELETED = 0
            AND D.CTX_ERROR_FLG = 0
            ORDER BY SCORE(1) DESC, D.CTX_TITLE
        '''

        selectSql = selectSql.format(ctx_search_text=ctx_search_text)

        exec_args = {'db_id': db_id}
        rst = db.session.execute(text(selectSql), exec_args)
        return rst
