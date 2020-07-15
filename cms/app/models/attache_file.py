from datetime import datetime

from sqlalchemy.sql import text

from app import db
from app.lib.cms_lib.str_util import StrUtil


class AttacheFile(db.Model):
    __tablename__ = 'PYTHON_ATTACHED_FILE'

    file_id = db.Column(db.Integer, primary_key=True)
    parent_object_id = db.Column(db.Integer, index=True)
    parent_object_type = db.Column(db.String(20))
    file_name = db.Column(db.String(400))
    file_size = db.Column(db.Integer)
    dir_name = db.Column(db.String(255))
    c_file_name = db.Column(db.String(20))
    c_file_size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(32))
    delete_flg = db.Column(db.Integer)
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.String(32))

    def __init__(self, parent_object_id=None, parent_object_type='AI'):
        self.parent_object_id = parent_object_id
        self.parent_object_type = parent_object_type
        self.delete_flg = 0

    def __repr__(self):
        return '<Name %r>' % (self.file_name)

    def setFileIdSeq(self, file_id):
        self.file_id = file_id

    def setAttacheFileInfo(self, file_id, file_name, file_size, dir_name, c_file_name, c_file_size):
        self.file_id = file_id
        self.file_name = file_name
        self.file_size = file_size
        self.dir_name = dir_name
        self.c_file_name = c_file_name
        self.c_file_size = c_file_size

    def setCreateInfo(self, created_by):
        self.created_by = created_by
        self.created_at = datetime.now()

    def setDeleteInfo(self, deleted_by):
        self.deleted_by = deleted_by
        self.deleted_at = datetime.now()

    def getAttacheFile(file_id):
        return db.session.query(AttacheFile).filter(AttacheFile.file_id == file_id).first()

    def chkExistsAttachedFile(af_obj):
        file = AttacheFile.getExistsAttachedFile(af_obj)
        if not file:
            return False

        af_obj.file_id = file.file_id
        StrUtil.print_debug('chkExistsAttachedFile fileId:[{}]'.format(str(af_obj.file_id)))
        return True

    def getExistsAttachedFile(af_obj):
        selectSql = '''
            SELECT rownum key, ATC.*
            FROM PYTHON_ATTACHED_FILE ATC
            WHERE ATC.PARENT_OBJECT_ID = :parentObjectId
            AND ATC.PARENT_OBJECT_TYPE = :parentObjectType
            AND ATC.FILE_NAME = :fileName
            AND ATC.DELETE_FLG = '0'
        '''

        t = text(selectSql)
        rst = db.session.execute(t,
                                 {'parentObjectId': af_obj.parent_object_id,
                                  'parentObjectType': af_obj.parent_object_type,
                                  'fileName': af_obj.file_name}).first()
        return rst
