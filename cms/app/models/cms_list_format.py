from app import db


class CmsListFormat(db.Model):
    __tablename__ = 'CMS_LIST_FORMAT'
    format_id = db.Column(db.Integer, primary_key=True)
    object_type_id = db.Column(db.Integer)
    format_type = db.Column(db.String(20))
    display_order = db.Column(db.Integer)
    remarks = db.Column(db.String(20))

    def getCmsListFormat(self, format_id):
        return db.session.query(CmsListFormat).filter(CmsListFormat.format_id == format_id).first()
