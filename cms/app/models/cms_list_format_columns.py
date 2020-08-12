from sqlalchemy.sql import text
from app import db


class CmsListFormatColumns(db.Model):
    __tablename__ = 'CMS_LIST_FORMAT_COLUMNS'
    format_id = db.Column(db.Integer, primary_key=True)
    display_order = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer)
    link_type = db.Column(db.String(100))
    link_type_id = db.Column(db.Integer)
    td_style = db.Column(db.String(100))
    link_format = db.Column(db.String(100))

    def __init__(self, format_id=None):
        self.format_id = format_id

    def getCmsListFormatColumns(self, format_id, display_order):
        return db.session.query(CmsListFormatColumns).filter(CmsListFormatColumns.format_id == format_id,
                                                             CmsListFormatColumns.display_order == display_order).first()

    def addCmsListFormatColumns(self, cmsListFormatColumns):
        return db.session.add(cmsListFormatColumns)

    def updateCmsListFormatColumns(self, cmsListFormatColumns):
        return cmsListFormatColumns

    def delCmsListFormatColumns(self, format_id):
        selectSql = '''
            DELETE FROM CMS_LIST_FORMAT_COLUMNS CLF
            WHERE CLF.FORMAT_ID = :format_id
        '''
        t = text(selectSql)
        db.session.execute(t, {'format_id': format_id})


    def getCmsListFormatColumnsList(self, format_id):
        selectSql = '''
            SELECT CO.FORMAT_ID, 
                CO.DISPLAY_ORDER, CO.PROPERTY_ID, COP.PROPERTY_NAME
            FROM CMS_LIST_FORMAT_COLUMNS CO , CMS_OBJECT_PROPERTY COP
            WHERE CO.PROPERTY_ID=COP.PROPERTY_ID
                AND CO.FORMAT_ID= :format_id
            ORDER BY CO.DISPLAY_ORDER
        '''
        t = text(selectSql)
        rst = db.session.execute(t, {'format_id': format_id})
        dic, array = {}, []
        for rowproxy in rst:
            for column, val in rowproxy.items():
                dic = {**dic, **{column: val}}
            array.append(dic)

        return array
