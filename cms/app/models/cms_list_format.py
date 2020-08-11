from app import db
from sqlalchemy.sql import text


class CmsListFormat(db.Model):
    __tablename__ = 'CMS_LIST_FORMAT'
    format_id = db.Column(db.Integer, primary_key=True)
    object_type_id = db.Column(db.Integer)
    format_type = db.Column(db.String(20))
    display_order = db.Column(db.Integer)
    remarks = db.Column(db.String(20))

    def __init__(self, format_id=None):
        self.format_id = format_id

    def addCmsListFormat(self, cmsListFormat):
        return db.session.add(cmsListFormat)

    def updateCmsListFormat(self, cmsListFormat):
        return cmsListFormat

    def delCmsListFormat(self, format_id):
        return db.session.query(CmsListFormat).filter(CmsListFormat.format_id == format_id).delete()

    def getCmsListFormat(self, format_id):
        return db.session.query(CmsListFormat).filter(CmsListFormat.format_id == format_id).first()

    def getCmsListFormatList(self, object_type_id, format_type):
        selectSql = '''
            SELECT 
                CLF.FORMAT_ID, 
                CLF.OBJECT_TYPE_ID, 
                CLF.FORMAT_TYPE, 
                CLF.DISPLAY_ORDER, 
                CLF.REMARKS
            FROM CMS_LIST_FORMAT CLF
            WHERE CLF.OBJECT_TYPE_ID = :object_type_id
                  AND CLF.FORMAT_TYPE = :format_type
             ORDER BY CLF.FORMAT_ID, CLF.DISPLAY_ORDER
        '''
        t = text(selectSql)
        return db.session.execute(t, {'object_type_id': object_type_id, 'format_type': format_type})
