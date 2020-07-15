from sqlalchemy.sql import text

from app import db


class CmsStyleMaster(db.Model):
    __tablename__ = 'CMS_STYLE_MASTER'
    style_name = db.Column(db.String(100), primary_key=True)
    style_type = db.Column(db.String(200))
    default_value = db.Column(db.String(200))
    remarks = db.Column(db.String(200))

    def getStyleSettings(self, db_id, style_type):
        selectSql = '''
            SELECT MST.STYLE_NAME, MST.STYLE_TYPE, NVL(STG.VALUE, MST.DEFAULT_VALUE) VALUE
              FROM CMS_STYLE_MASTER MST
              LEFT JOIN CMS_STYLE_SETTING STG
                ON MST.STYLE_NAME = STG.STYLE_NAME
               AND STG.DB_ID = :db_id
             WHERE MST.STYLE_TYPE = :style_type
        '''
        rst = db.session.execute(text(selectSql), {'db_id': db_id, 'style_type': style_type})
        dic = {}
        for row in rst:
            dic = {**dic, **{row.style_name: row.value}}
        return dic
