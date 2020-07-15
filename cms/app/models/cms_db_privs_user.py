from datetime import datetime

from sqlalchemy.sql import text

from app import db


class CmsDbPrivsUser(db.Model):
    __tablename__ = 'CMS_DB_PRIVS_USER'

    db_id = db.Column(db.Integer, primary_key=True)
    management_corp_cd = db.Column(db.String(3), primary_key=True)
    dept_cd = db.Column(db.String(10), primary_key=True)
    tuid = db.Column(db.String(11), primary_key=True)
    privs_type = db.Column(db.String(10))
    is_deleted = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    created_by = db.Column(db.String(10))
    updated_at = db.Column(db.DateTime)
    updated_by = db.Column(db.String(10))
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.String(10))

    def __init__(self, db_id=None, management_corp_cd=None, dept_cd=None, tuid=None, privs_type=None):
        self.db_id = db_id
        self.management_corp_cd = management_corp_cd
        self.dept_cd = dept_cd
        self.tuid = tuid
        self.privs_type = privs_type
        self.is_deleted = 0

    def getPrivsUser(self, db_id, management_corp_cd, dept_cd, tuid, privs_type):
        selectSql = '''
            SELECT T.*, CASE WHEN T.CORP_DEPT_CD = '%:%' THEN 'ALL' ELSE T.DEPT_NAME END DEPT_NAME
            FROM (
                SELECT MANAGEMENT_CORP_CD || ':' || DEPT_CD CORP_DEPT_CD, MANAGEMENT_CORP_CD CORP_CD, DEPT_CD, TUID, PRIVS_TYPE,
                (SELECT MAX(U.L_LANG_FAMILY_NAME || ' ' || U.L_LANG_FIRST_NAME)
                  FROM CMS_USER_MASTER U
                  WHERE U.TUID = PU.TUID) USER_NAME,
                (SELECT LIST_COLLECT(CAST (COLLECT(U.MANAGEMENT_CORP_ABB_NAME || U.DEPT_ABB_NAME) AS VARCHAR2_ARRAY), ',')
                  FROM CMS_USER_MASTER U
                  WHERE U.MANAGEMENT_CORP_CD LIKE PU.MANAGEMENT_CORP_CD
                  AND U.DEPT_CD LIKE PU.DEPT_CD
                  AND U.TUID = PU.TUID) DEPT_NAME
                FROM CMS_DB_PRIVS_USER PU
                WHERE PU.DB_ID = :db_id
                AND PU.MANAGEMENT_CORP_CD = :management_corp_cd
                AND PU.DEPT_CD = :dept_cd
                AND PU.TUID = :tuid
                AND PU.PRIVS_TYPE = :privs_type
                AND PU.IS_DELETED = 0
            ) T
        '''

        return db.session.execute(
            text(selectSql),
            {'db_id': db_id, 'management_corp_cd': management_corp_cd,
             'dept_cd': dept_cd, 'tuid': tuid, 'privs_type': privs_type}).first()

    def getPrivsUserList(self, form):
        selectSql = '''
        　　　SELECT T.*, CASE WHEN T.DEPT_NAME IS NULL THEN 'bg_gray' ELSE '' END CSS_NAME
            FROM (
                SELECT MANAGEMENT_CORP_CD CORP_CD, DEPT_CD, TUID, PRIVS_TYPE,
                     (SELECT MAX(U.L_LANG_FAMILY_NAME || ' ' || U.L_LANG_FIRST_NAME)
                      FROM CMS_USER_MASTER U
                      WHERE U.TUID = PU.TUID) USER_NAME,
                     (SELECT LIST_COLLECT(CAST (COLLECT(U.MANAGEMENT_CORP_ABB_NAME || U.DEPT_ABB_NAME) AS VARCHAR2_ARRAY), ',')
                      FROM CMS_USER_MASTER U
                      WHERE U.MANAGEMENT_CORP_CD LIKE PU.MANAGEMENT_CORP_CD
                      AND U.DEPT_CD LIKE PU.DEPT_CD
                      AND U.TUID = PU.TUID) DEPT_NAME,
                     (SELECT MAX(L.OPERATION_DATE) FROM CMS_OPERATION_LOG L
                      WHERE L.DB_ID = PU.DB_ID
                      AND L.USER_ID = PU.TUID) LAST_LOGIN_DATE
                FROM CMS_DB_PRIVS_USER PU
                WHERE PU.DB_ID = :db_id
                AND PU.IS_DELETED = 0
                ORDER BY DEPT_NAME
            ) T
        '''

        rst = db.session.execute(text(selectSql), {'db_id': form["db_id"]})
        return rst

    def addPrivsUser(self, cmsDbPrivsUser, user_id):
        cmsDbPrivsUser.is_deleted = 0
        cmsDbPrivsUser.created_by = user_id
        cmsDbPrivsUser.created_at = datetime.now()
        cmsDbPrivsUser.updated_by = user_id
        cmsDbPrivsUser.updated_at = datetime.now()
        return db.session.add(cmsDbPrivsUser)

    def uptPrivsUser(self, db_id, old_corp_cd, old_dept_cd, tuid, old_privs_type, corp_cd, dept_cd, privs_type,
                     user_id):
        updateSql = '''
            UPDATE CMS_DB_PRIVS_USER PU
            SET PU.MANAGEMENT_CORP_CD = :corp_cd,
                PU.DEPT_CD = :dept_cd,
                PU.UPDATED_AT = SYSDATE,
                PU.UPDATED_BY = :user_id
            WHERE PU.IS_DELETED = 0
            AND PU.DB_ID = :db_id
            AND PU.MANAGEMENT_CORP_CD = :old_corp_cd
            AND PU.DEPT_CD = :old_dept_cd
            AND PU.TUID = :tuid
            AND PU.PRIVS_TYPE = :old_privs_type
        '''
        db.session.execute(
            text(updateSql),
            {'db_id': db_id, 'old_corp_cd': old_corp_cd, 'old_dept_cd': old_dept_cd, 'tuid': tuid,
             'old_privs_type': old_privs_type, 'corp_cd': corp_cd, 'dept_cd': dept_cd, 'user_id': user_id})

    def delPrivsUser(self, db_id, corp_cd, dept_cd, tuid, privs_type, user_id):
        deleteSql = '''
            UPDATE CMS_DB_PRIVS_USER PU
            SET PU.IS_DELETED = 1,
                PU.DELETED_AT = SYSDATE,
                PU.DELETED_BY = :user_id
            WHERE PU.IS_DELETED = 0
            AND PU.DB_ID = :db_id
            AND PU.MANAGEMENT_CORP_CD = :corp_cd
            AND PU.DEPT_CD = :dept_cd
            AND PU.TUID = :tuid
            AND PU.PRIVS_TYPE = :privs_type
        '''
        db.session.execute(
            text(deleteSql),
            {'db_id': db_id, 'corp_cd': corp_cd, 'dept_cd': dept_cd, 'tuid': tuid,
             'privs_type': privs_type, 'user_id': user_id})
