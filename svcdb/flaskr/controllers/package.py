﻿from flask import current_app

from flaskr import db
from flaskr.lib.conf.const import Const
from flaskr.lib.svcdb_lib.str_util import StrUtil


class PkgUserAuth():
    def check_passwd_for_svcdb(user_id, password):
        package_name = 'pkg_user_auth'
        if StrUtil.get_safe_config(current_app, 'PROJECT_STAGE') == Const.DEVELOPMENT:
            package_name = 'pkg_user_auth_debug'

        current_sqlalchemy_echo = StrUtil.get_safe_config(current_app, 'SQLALCHEMY_ECHO')

        # 認証SQLのログを出力しないようにする
        db.session.bind.echo = False

        returnVal = db.session.execute(
            'select ' + package_name + '.check_passwd_for_svcdb(:user_id, :password) as val from dual',
            {'user_id': user_id, 'password': password}).fetchone().val

        # 現状設定に戻す
        db.session.bind.echo = current_sqlalchemy_echo

        if returnVal == 0:
            return True
        return False


class PkgSvcdbSecurity():
    # パッケージ
    def __init__(self, package_name='pkg_svcdb_security'):
        self.package_name = package_name

    def isDbVisible(self, db_id, user_id):
        returnVal = db.session.execute(
            'select ' + self.package_name + '.is_db_visible(:db_id, :user_id) as val from dual',
            {'db_id': db_id, 'user_id': user_id}).fetchone().val
        if returnVal == 1:
            return True
        return False

    def isFolderVisible(self, folder_id, user_id):
        returnVal = db.session.execute(
            'select ' + self.package_name + '.is_folder_visible(:folder_id, :user_id) as val from dual',
            {'folder_id': folder_id, 'user_id': user_id}).fetchone().val
        if returnVal == 1:
            return True
        return False

    def isObjectVisible(self, object_id, user_id):
        returnVal = db.session.execute(
            'select ' + self.package_name + '.is_object_visible(:object_id, :user_id) as val from dual',
            {'object_id': object_id, 'user_id': user_id}).fetchone().val
        if returnVal == 1:
            return True
        return False

    def isFileVisible(self, file_id, user_id):
        returnVal = db.session.execute(
            'select ' + self.package_name + '.is_file_visible(:file_id, :user_id) as val from dual',
            {'file_id': file_id, 'user_id': user_id}).fetchone().val
        if returnVal == 1:
            return True
        return False

    def isDbEditable(self, db_id, user_id):
        returnVal = db.session.execute(
            'select ' + self.package_name + '.is_db_editable(:db_id, :user_id) as val from dual',
            {'db_id': db_id, 'user_id': user_id}).fetchone().val
        if returnVal == 1:
            return True
        return False

    def isAdminUser(self, user_id):
        returnVal = db.session.execute(
            'select ' + self.package_name + '.is_admin_user(:user_id) as val from dual',
            {'user_id': user_id}).fetchone().val
        if returnVal == 1:
            return True
        return False


class PkgIpAddrUtil():
    # パッケージ
    def __init__(self, package_name='pkg_ip_addr_util'):
        self.package_name = package_name

    def isDbIpAddrVisible(self, db_id, ip_addr):
        returnVal = db.session.execute(
            'select ' + self.package_name + '.check_db_ip_addr_security(:db_id, :ip_addr) as val from dual',
            {'db_id': db_id, 'ip_addr': ip_addr}).fetchone().val
        if returnVal == 1:
            return True
        return False


class PkgSvcdbLog():
    # パッケージ
    def __init__(self, package_name='pkg_svcdb_log'):
        self.package_name = package_name

    def saveOperationLog(self, user_id, db_id, operation_cd, object_id='', object_type='', note=''):
        return;
        ip_addr = StrUtil.get_ip_addr()
        db.session.execute(
            'begin '
            + self.package_name + '.save_operation_log'
            + '(:user_id, :operation_cd, :object_id, :object_type, :db_id, :note, :ip_addr); '
            + 'end;',
            {'user_id': user_id,
             'operation_cd': operation_cd,
             'object_id': object_id,
             'object_type': object_type,
             'db_id': db_id,
             'note': note,
             'ip_addr': ip_addr})
