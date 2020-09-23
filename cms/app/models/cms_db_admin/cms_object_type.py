from werkzeug.exceptions import abort

from app import db
from sqlalchemy.sql import text


class CmsObjectType(db.Model):
    __tablename__ = 'CMS_OBJECT_TYPE'
    object_type_id = db.Column(db.Integer, primary_key=True)
    object_type_name = db.Column(db.String(100))
    db_id = db.Column(db.Integer)
    display_order = db.Column(db.Integer)
    remarks = db.Column(db.String(2000))
    ctx_flg = db.Column(db.Integer)
    ctx_title_format = db.Column(db.String(100))
    log_notes_format = db.Column(db.String(100))

    def get_login_message(self):
        return self.login_message

    @staticmethod
    def getCmsObjectType(db_id, object_type_id):
        obj = db.session.query(CmsObjectType).filter(CmsObjectType.db_id == db_id,
                                                     CmsObjectType.object_type_id == object_type_id).first()
        if obj is None:
            abort(404)
        return obj

    @staticmethod
    def getObjectTypeList(db_id):
        selectSql = '''
            SELECT 
                COT.OBJECT_TYPE_ID, 
                COT.OBJECT_TYPE_NAME, 
                COT.DB_ID, 
                COT.DISPLAY_ORDER, 
                COT.REMARKS,
                COT.CTX_FLG
            FROM CMS_OBJECT_TYPE COT
            WHERE COT.DB_ID = :db_id
            ORDER BY COT.DISPLAY_ORDER
        '''
        t = text(selectSql)
        rst = db.session.execute(t, {'db_id': db_id})
        return rst
    @staticmethod
    def getObjectType(db_id):
        return db.session.query(CmsObjectType).filter(CmsObjectType.db_id == db_id).first()
