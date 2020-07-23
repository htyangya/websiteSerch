from app import db


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
    def getCmsObjectType(object_type_id):
        return db.session.query(CmsObjectType).get_or_404(object_type_id)

    @staticmethod
    def getObjectTypeList(db_id):
        return db.session.query(CmsObjectType).filter(CmsObjectType.db_id == db_id).all()
