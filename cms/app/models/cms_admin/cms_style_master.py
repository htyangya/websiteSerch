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

    def getStyleSettingList(self, db_id):
        selectSql = '''
            SELECT M.STYLE_NAME,
                M.STYLE_TYPE,
                NVL(S.VALUE, M.DEFAULT_VALUE) VALUE,
                M.DEFAULT_VALUE,
                M.REMARKS
            FROM CMS_STYLE_MASTER M
            LEFT OUTER JOIN CMS_STYLE_SETTING S
            ON (M.STYLE_NAME = S.STYLE_NAME
                AND S.DB_ID = :db_id)
            ORDER BY M.STYLE_NAME
        '''
        t = text(selectSql)
        return db.session.execute(t, {'db_id': db_id})

    def getStyleSettingInfo(self, db_id, style_name):
        selectSql = '''
            SELECT M.STYLE_NAME,
                M.STYLE_TYPE,
                S.VALUE ,
                M.DEFAULT_VALUE,
                M.REMARKS
            FROM CMS_STYLE_MASTER M
                LEFT OUTER JOIN CMS_STYLE_SETTING S
                ON (M.STYLE_NAME = S.STYLE_NAME
                AND S.DB_ID = :db_id)
            WHERE M.STYLE_NAME = :style_name
        '''
        t = text(selectSql)
        rst = db.session.execute(t, {'db_id': db_id, 'style_name': style_name}).first()
        return rst
