from sqlalchemy.sql import text

from flaskr import db


class SvcdbTurbineMasterTable(db.Model):
    __tablename__ = 'TURBINE_MASTER_TABLE'

    master_kind = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, primary_key=True)

    def get_master_list(self, master_kind):
        selectSql = '''
            SELECT TMT.CODE, TMT.DATA1
            FROM TURBINE_MASTER_TABLE TMT
            WHERE TMT.MASTER_KIND = :master_kind
            ORDER BY TMT.DISPLAY_ORDER, TMT.DATA1, TMT.DATA2
        '''

        t = text(selectSql)
        return db.session.execute(t, {'master_kind': master_kind})
