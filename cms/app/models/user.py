from flask_login import UserMixin
from sqlalchemy.sql import text

from app import db, login_manager


# UserMixinを継承した Userクラスを作る
class User(UserMixin, db.Model):
    __tablename__ = 'CMS_USER_MASTER'
    tuid = db.Column(db.String(11), primary_key=True)
    l_lang_family_name = db.Column(db.String(20))
    l_lang_first_name = db.Column(db.String(20))
    alias_mail_address = db.Column(db.String(80))
    dept_abb_name = db.Column(db.String(240))
    management_corp_cd = db.Column(db.String(3))
    dept_cd = db.Column(db.String(10))

    def __init__(self, tuid=None, password=None):
        self.tuid = tuid
        self.is_authenticated = False

    def is_authenticated(self):
        return self.is_authenticated

    def __repr__(self):
        return '<Name %r>' % (self.tuid)

    def check_password(self, password):
        return True

    def get_id(self):
        return self.tuid

    def get_user_name(self):
        return self.l_lang_family_name + ' ' + self.l_lang_first_name

    def getUserInfo(user_id):
        selectSql = '''
            SELECT TUID, ADDITIONAL_SEQ, PERSON_FAMILY_NAME, PERSON_FIRST_NAME,
                L_LANG_FAMILY_NAME, L_LANG_FIRST_NAME, MANAGEMENT_CORP_CD,
                MANAGEMENT_CORP_ABB_NAME, MANAGEMENT_CORP_ABB_NAME_EN, CORP_CD,
                EMP_TYPE_CD, DIV_CD, DEPT_CD, DEPT_ABB_NAME1, DEPT_ABB_NAME2,
                DEPT_ABB_NAME3, DEPT_NAME1_EN, DEPT_NAME2_EN, DEPT_NAME3_EN,
                DEPT_ABB_NAME, TITLE_CD, TITLE_NAME, TITLE_NAME_EN, ALIAS_MAIL_ADDRESS
            FROM CMS_USER_MASTER T
            WHERE T.TUID = :tuid
        '''
        t = text(selectSql)
        return db.session.execute(t, {'tuid': user_id}).first()

    def getUserDeptList(user_id):
        selectSql = '''
            SELECT MANAGEMENT_CORP_CD CORP_CD, DEPT_ABB_NAME, DEPT_CD,
                (SELECT LIST_COLLECT(CAST (COLLECT(U.MANAGEMENT_CORP_ABB_NAME || U.DEPT_ABB_NAME) AS VARCHAR2_ARRAY), ',')
                 FROM CMS_USER_MASTER U
                 WHERE U.MANAGEMENT_CORP_CD LIKE T.MANAGEMENT_CORP_CD
                 AND U.DEPT_CD LIKE T.DEPT_CD
                 AND U.TUID = T.TUID) DEPT_NAME
            FROM CMS_USER_MASTER T
            WHERE T.TUID = :tuid
        '''
        t = text(selectSql)
        rst = db.session.execute(t, {'tuid': user_id})

        dic, array = {}, []
        for rowproxy in rst:
            for column, val in rowproxy.items():
                dic = {**dic, **{column: val}}
            array.append(dic)

        return array


# @login_manager.user_loaderで認証ユーザーの呼び出し方を定義する
@login_manager.user_loader
def load_user(user_id):
    #    return User.getUserInfo(user_id)
    return User.query.get(user_id)
