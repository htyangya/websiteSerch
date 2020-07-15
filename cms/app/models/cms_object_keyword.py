from sqlalchemy.sql import text

from app import db


class CmsObjectKeyword(db.Model):
    __tablename__ = 'CMS_OBJECT_KEYWORD'
    object_id = db.Column(db.Integer, primary_key=True)
    keyword_id = db.Column(db.Integer, primary_key=True)
    db_column_name = db.Column(db.String(30))

    def __init__(self, keyword=None):
        self.keyword = keyword

    def getObjectKeyword(self, object_id, keyword_id):
        return db.session.query(CmsObjectKeyword).filter(CmsObjectKeyword.object_id == object_id,
                                                         CmsObjectKeyword.keyword_id == keyword_id).first()

    def getObjectKeywordList(self, object_id, db_column_name):
        return db.session.query(CmsObjectKeyword).filter(CmsObjectKeyword.object_id == object_id,
                                                         CmsObjectKeyword.db_column_name == db_column_name).all()

    def addObjectKeyword(self, cmsObjectKeywoed):
        return db.session.add(cmsObjectKeywoed)

    def deleteObjectKeywordList(self, object_id):
        return db.session.query(CmsObjectKeyword).filter(CmsObjectKeyword.object_id == object_id).delete()

    def deleteObjectKeyword(self, object_id, keyword_id):
        return db.session.query(CmsObjectKeyword).filter(CmsObjectKeyword.object_id == object_id,
                                                         CmsObjectKeyword.keyword_id == keyword_id).delete()

    def getObjectIdList(self, keyword_id):
        selectSql = '''
              SELECT T.OBJECT_ID,
                     T.DB_COLUMN_NAME,
                     T.KEYWORD_ID
              FROM CMS_OBJECT_KEYWORD T
             WHERE T.KEYWORD_ID = :keyword_id
        '''
        t = text(selectSql)
        rst = db.session.execute(t, {'keyword_id': keyword_id})
        array = []
        for rowproxy in rst:
            array.append(rowproxy.object_id)
        return array
