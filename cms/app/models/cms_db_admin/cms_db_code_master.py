from sqlalchemy.sql import text

from app import db


class CmsDbCodeMaster(db.Model):
    __tablename__ = 'CMS_CODE_MASTER'

    master_kind = db.Column(db.String(100), primary_key=True)
    code = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(500))
    display_order = db.Column(db.Integer)

    def getCodeMasterList(self, master_kind):
        selectSql = '''
            SELECT MASTER_KIND, CODE, NAME, DISPLAY_ORDER
            FROM CMS_CODE_MASTER C
            WHERE C.MASTER_KIND = :master_kind
        '''

        rst = db.session.execute(text(selectSql), {'master_kind': master_kind})
        return rst

    def checkCorpCdExist(self, corp_cd):
        selectSql = '''
            SELECT COUNT(*) cnt
            FROM CMS_CORP_MASTER C
            WHERE C.CORP_CD = :corp_cd
        '''

        exec_args = {"corp_cd": corp_cd}
        rst = db.session.execute(text(selectSql), exec_args).first()
        return rst.cnt > 0

    def getCorpListCnt(self, search_cond):
        selectSql = '''
            SELECT COUNT(*) cnt
            FROM CMS_CORP_MASTER C
            WHERE C.CORP_CD LIKE '%' || '{search_cond}' || '%'
            OR C.CORP_ABB_NAME LIKE '%' || '{search_cond}' || '%'
            OR C.CORP_ABB_NAME LIKE '%' || '{search_cond}' || '%'
        '''

        selectSql = selectSql.format(search_cond=search_cond)
        exec_args = {}
        rst = db.session.execute(text(selectSql), exec_args).first()
        return rst.cnt

    def getCorpList(self, search_cond):
        selectSql = '''
            SELECT C.CORP_CD, NVL(C.CORP_ABB_NAME, C.CORP_NAME) CORP_NAME
            FROM CMS_CORP_MASTER C
            WHERE C.CORP_CD LIKE '%' || '{search_cond}' || '%'
            OR C.CORP_ABB_NAME LIKE '%' || '{search_cond}' || '%'
            OR C.CORP_ABB_NAME LIKE '%' || '{search_cond}' || '%'
        '''
        selectSql = selectSql.format(search_cond=search_cond)
        return db.session.execute(text(selectSql), {})
