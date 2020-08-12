from sqlalchemy.sql import text
from app import db

class CmsListFormatSort(db.Model):
    __tablename__ = 'CMS_LIST_FORMAT_SORT'
    format_id = db.Column(db.Integer, primary_key=True)
    display_order = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer)
    sort_key_order = db.Column(db.String(10))

    def __init__(self, format_id=None):
        self.format_id = format_id

    def getCmsListFormatSort(self, format_id, display_order):
        return db.session.query(CmsListFormatSort).filter(CmsListFormatSort.format_id == format_id,
                                                          CmsListFormatSort.display_order == display_order).first()

    def addCmsListFormatColumns(self, cmsListFormatSort):
        return db.session.add(cmsListFormatSort)

    def updateCmsListFormatSort(self, cmsListFormatSort):
        return cmsListFormatSort

    def delCmsListFormatSort(self, format_id):
        selectSql = '''
                DELETE FROM CMS_LIST_FORMAT_SORT CLF
                WHERE CLF.FORMAT_ID = :format_id
        '''
        t = text(selectSql)
        db.session.execute(t, {'format_id': format_id})

    def getCmsListFormatSortList(self, format_id):
        selectSql = '''
            SELECT SO.FORMAT_ID, 
                SO.DISPLAY_ORDER, SO.PROPERTY_ID, SO.SORT_KEY_ORDER
            FROM CMS_LIST_FORMAT_SORT SO
            WHERE SO.FORMAT_ID= :format_id
            ORDER BY SO.DISPLAY_ORDER
        '''
        t = text(selectSql)
        rst = db.session.execute(t, {'format_id': format_id})
        dic, array = {}, []
        for rowproxy in rst:
            for column, val in rowproxy.items():
                dic = {**dic, **{column: val}}
            array.append(dic)
        return array
