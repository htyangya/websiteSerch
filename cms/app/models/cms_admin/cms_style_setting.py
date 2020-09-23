from sqlalchemy.sql import text

from app import db


class CmsStyleSetting(db.Model):
    __tablename__ = 'CMS_STYLE_SETTING'
    db_id = db.Column(db.Integer, primary_key=True)
    style_name = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.String(200))

    def updateStyleSetting(self, db_id, style_name, value):
        selectSql = '''
            MERGE INTO CMS_STYLE_SETTING CSS
            USING (
                SELECT '{db_id}' DB_ID, '{style_name}' STYLE_NAME, '{value}' VALUE
                FROM DUAL
            ) P
            ON (CSS.DB_ID = P.DB_ID
                AND CSS.STYLE_NAME = P.STYLE_NAME)
            -- 既存レコードの更新
            WHEN MATCHED THEN
                UPDATE SET VALUE = P.VALUE
            -- 新規レコードの作成
            WHEN NOT MATCHED THEN
                INSERT (
                    DB_ID,
                    STYLE_NAME,
                    VALUE
                ) VALUES (
                    P.DB_ID,
                    P.STYLE_NAME,
                    P.VALUE
                )
        '''
        selectSql = selectSql.format(db_id=db_id, style_name=style_name, value=value)
        t = text(selectSql)
        db.session.execute(t)
