from datetime import datetime

from sqlalchemy.sql import text

from app import db


class CmsDbPrivsDept(db.Model):
    __tablename__ = 'CMS_DB_PRIVS_DEPT'

    db_id = db.Column(db.Integer, primary_key=True)
    management_corp_cd = db.Column(db.String(3), primary_key=True)
    div_cd = db.Column(db.String(2), primary_key=True)
    dept_cd = db.Column(db.String(10))
    emp_type_cd = db.Column(db.String(2), primary_key=True)
    working_type_cd = db.Column(db.String(2))
    privs_type = db.Column(db.String(10))
    is_deleted = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    created_by = db.Column(db.String(10))
    updated_at = db.Column(db.DateTime)
    updated_by = db.Column(db.String(10))
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.String(10))

    def __init__(self, db_id=None, management_corp_cd=None, div_cd=None, dept_cd=None, emp_type_cd=None,
                 working_type_cd=None, privs_type=None):
        self.db_id = db_id
        self.management_corp_cd = management_corp_cd
        self.div_cd = div_cd
        self.dept_cd = dept_cd
        self.emp_type_cd = emp_type_cd
        self.working_type_cd = working_type_cd
        self.privs_type = privs_type
        self.is_deleted = 0

    def getPrivsDept(self, db_id, management_corp_cd, div_cd, dept_cd, emp_type_cd, working_type_cd, privs_type):
        selectSql = '''
            SELECT PD.MANAGEMENT_CORP_CD CORP_CD,
                (SELECT NVL(C.CORP_ABB_NAME, C.CORP_NAME)
                 FROM CMS_CORP_MASTER C
                 WHERE C.CORP_CD = PD.MANAGEMENT_CORP_CD) CORP_NAME, 
                DIV_CD, DEPT_CD, EMP_TYPE_CD,
                DECODE(EMP_TYPE_CD,  '%', 'ALL',
                    (SELECT C.NAME
                     FROM CMS_CODE_MASTER C
                     WHERE C.MASTER_KIND = 'EMP_TYPE_CD'
                     AND C.CODE = PD.EMP_TYPE_CD)) EMP_TYPE_NAME, WORKING_TYPE_CD,
                DECODE(WORKING_TYPE_CD,  '%', 'ALL',
                    (SELECT C.NAME
                     FROM CMS_CODE_MASTER C
                     WHERE C.MASTER_KIND = 'WORKING_TYPE_CD'
                     AND C.CODE = PD.WORKING_TYPE_CD)) WORKING_TYPE_NAME, PRIVS_TYPE
            FROM CMS_DB_PRIVS_DEPT PD
            WHERE PD.DB_ID = :db_id
            AND PD.MANAGEMENT_CORP_CD = :management_corp_cd
            AND PD.DIV_CD = :div_cd
            AND PD.DEPT_CD = :dept_cd
            AND PD.EMP_TYPE_CD = :emp_type_cd
            AND PD.WORKING_TYPE_CD = :working_type_cd
            AND PD.PRIVS_TYPE = :privs_type
            AND PD.IS_DELETED = 0
        '''

        return db.session.execute(
            text(selectSql),
            {'db_id': db_id, 'management_corp_cd': management_corp_cd,
             'div_cd': div_cd, 'dept_cd': dept_cd, 'emp_type_cd': emp_type_cd,
             'working_type_cd': working_type_cd, 'privs_type': privs_type}).first()

    def getPrivsDeptList(self, form):
        selectSql = '''
        　　　SELECT PD.MANAGEMENT_CORP_CD CORP_CD,
                (SELECT NVL(C.CORP_ABB_NAME, C.CORP_NAME)
                 FROM CMS_CORP_MASTER C
                 WHERE C.CORP_CD = PD.MANAGEMENT_CORP_CD) CORP_NAME,
                DIV_CD, DEPT_CD, EMP_TYPE_CD,
                DECODE(EMP_TYPE_CD,  '%', 'ALL',
                    (SELECT C.NAME
                     FROM CMS_CODE_MASTER C
                     WHERE C.MASTER_KIND = 'EMP_TYPE_CD'
                     AND C.CODE = PD.EMP_TYPE_CD)
                ) EMP_TYPE_NAME, WORKING_TYPE_CD,
                DECODE(WORKING_TYPE_CD,  '%', 'ALL', 
                    (SELECT C.NAME
                     FROM CMS_CODE_MASTER C
                     WHERE C.MASTER_KIND = 'WORKING_TYPE_CD'
                     AND C.CODE = PD.WORKING_TYPE_CD)
                ) WORKING_TYPE_NAME, PRIVS_TYPE
            FROM CMS_DB_PRIVS_DEPT PD
            WHERE PD.DB_ID = :db_id
            AND PD.IS_DELETED = 0
        '''

        rst = db.session.execute(text(selectSql), {'db_id': form["db_id"]})
        return rst

    def addPrivsDept(self, cmsDbPrivsDept, user_id):
        cmsDbPrivsDept.is_deleted = 0
        cmsDbPrivsDept.created_by = user_id
        cmsDbPrivsDept.created_at = datetime.now()
        cmsDbPrivsDept.updated_by = user_id
        cmsDbPrivsDept.updated_at = datetime.now()
        return db.session.add(cmsDbPrivsDept)

    def uptPrivsDept(self, db_id, management_corp_cd, div_cd, dept_cd, emp_type_cd, working_type_cd, old_div_cd,
                     old_dept_cd, old_emp_type_cd, old_working_type_cd, old_privs_type, user_id):
        updateSql = '''
            UPDATE CMS_DB_PRIVS_DEPT PD
            SET PD.DIV_CD = :div_cd,
                PD.DEPT_CD = :dept_cd,
                PD.EMP_TYPE_CD = :emp_type_cd,
                PD.WORKING_TYPE_CD = :working_type_cd,
                PD.UPDATED_AT = SYSDATE,
                PD.UPDATED_BY = :user_id
            WHERE PD.DB_ID = :db_id
            AND PD.MANAGEMENT_CORP_CD = :management_corp_cd
            AND PD.DIV_CD = :old_div_cd
            AND PD.DEPT_CD = :old_dept_cd
            AND PD.EMP_TYPE_CD = :old_emp_type_cd
            AND PD.WORKING_TYPE_CD = :old_working_type_cd
            AND PD.PRIVS_TYPE = :old_privs_type
            AND PD.IS_DELETED = 0
        '''

        db.session.execute(
            text(updateSql),
            {'db_id': db_id, 'management_corp_cd': management_corp_cd, 'div_cd': div_cd, 'dept_cd': dept_cd,
             'emp_type_cd': emp_type_cd, 'working_type_cd': working_type_cd, 'old_div_cd': old_div_cd,
             'old_dept_cd': old_dept_cd, 'old_emp_type_cd': old_emp_type_cd, 'old_working_type_cd': old_working_type_cd,
             'old_privs_type': old_privs_type, 'user_id': user_id})

    def delPrivsDept(self, db_id, management_corp_cd, div_cd, dept_cd, emp_type_cd, working_type_cd, privs_type,
                     user_id):
        deleteSql = '''
            UPDATE CMS_DB_PRIVS_DEPT PD
            SET PD.IS_DELETED = 1,
                PD.DELETED_AT = SYSDATE,
                PD.DELETED_BY = :user_id
            WHERE PD.DB_ID = :db_id
            AND PD.MANAGEMENT_CORP_CD = :management_corp_cd
            AND PD.DIV_CD = :div_cd
            AND PD.DEPT_CD = :dept_cd
            AND PD.EMP_TYPE_CD = :emp_type_cd
            AND PD.WORKING_TYPE_CD = :working_type_cd
            AND PD.PRIVS_TYPE = :privs_type
            AND PD.IS_DELETED = 0
        '''

        db.session.execute(
            text(deleteSql),
            {'db_id': db_id, 'management_corp_cd': management_corp_cd, 'div_cd': div_cd, 'dept_cd': dept_cd,
             'emp_type_cd': emp_type_cd, 'working_type_cd': working_type_cd, 'privs_type': privs_type,
             'user_id': user_id})
