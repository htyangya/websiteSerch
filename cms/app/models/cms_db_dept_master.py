from sqlalchemy.sql import text

from app import db


class CmsDbDeptMaster(db.Model):
    __tablename__ = 'CMS_DEPT_MASTER'

    corp_cd = db.Column(db.String(3), primary_key=True)
    dept_cd = db.Column(db.String(10), primary_key=True)
    upper_dept_cd = db.Column(db.String(60))
    div_cd = db.Column(db.String(2))
    div_sub_cd = db.Column(db.String(2))
    dept_abb_name1 = db.Column(db.String(30))
    dept_abb_name2 = db.Column(db.String(30))
    dept_abb_name3 = db.Column(db.String(30))
    full_dept_name = db.Column(db.String(90))
    disp_dept_name = db.Column(db.String(30))

    def getDeptMasterList(self, form):
        selectSql = '''
            SELECT C.CORP_CD, NVL(C.CORP_ABB_NAME, C.CORP_NAME) CORP_NAME, D.DEPT_CD, D.FULL_DEPT_NAME
            FROM CMS_DEPT_MASTER D, CMS_CORP_MASTER C
            WHERE C.CORP_CD = D.CORP_CD
            AND D.CORP_CD = :corp_cd
            AND D.DIV_CD LIKE :div_cd
            AND D.DEPT_CD LIKE :dept_cd
        '''

        rst = db.session.execute(text(selectSql),
                                 {'corp_cd': form["corp_cd"], 'div_cd': form["div_cd"], 'dept_cd': form["dept_cd"]})
        return rst
