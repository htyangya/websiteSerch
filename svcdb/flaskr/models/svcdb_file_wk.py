from datetime import datetime

from sqlalchemy.sql import text

from flaskr import db


class SvcdbFileWk(db.Model):
    __tablename__ = 'SVCDB_FILE_WK'

    edit_id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, primary_key=True)
    parent_object_id = db.Column(db.Integer, index=True)
    file_type_id = db.Column(db.Integer)
    file_name = db.Column(db.String(400))
    file_size = db.Column(db.Integer)
    dir_name = db.Column(db.String(255))
    c_file_name = db.Column(db.String(20))
    c_file_size = db.Column(db.Integer)
    is_deleted = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(32))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.String(32))
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.String(32))

    SELECT_COLUMN_STR = '''
        EDIT_ID, FILE_ID, PARENT_OBJECT_ID, FILE_TYPE_ID, FILE_NAME,
        CASE WHEN UPPER(SUBSTRB(FILE_NAME, -3)) = 'PDF' THEN '1' ELSE '0' END IS_PDF_FLG,
        CASE WHEN FILE_SIZE IS NULL THEN ''
             WHEN FILE_SIZE > 1024 * 1024 THEN
                  CEIL(FILE_SIZE / (1024 * 1024)) || 'MB'
             ELSE CEIL(FILE_SIZE / 1024) || 'KB' END FILE_SIZE_DISP,
        FILE_SIZE, DIR_NAME, C_FILE_NAME, C_FILE_SIZE, IS_DELETED,
        TO_CHAR(UPDATED_AT, 'YYYY/MM/DD') UPDATED_AT_STR,
        UPDATED_BY,
        TO_CHAR(CREATED_AT, 'YYYY/MM/DD') CREATED_AT_STR,
        CREATED_BY
    '''

    def __init__(self, parent_object_id=None):
        self.parent_object_id = parent_object_id
        self.is_deleted = 0

    def __repr__(self):
        return '<Name %r>' % (self.file_name)

    def getFile(self, edit_id, file_id):
        return db.session.query(SvcdbFileWk).filter(SvcdbFileWk.edit_id == edit_id,
                                                  SvcdbFileWk.file_id == file_id,
                                                  SvcdbFileWk.is_deleted == 0).first()

    def getFileList(self, edit_id, parent_object_id, file_type_id=None):
        query = db.session.query(SvcdbFileWk).filter(SvcdbFileWk.edit_id == edit_id,
                                                   SvcdbFileWk.parent_object_id == parent_object_id)
        if file_type_id != None and file_type_id > 0:
            query = query.filter(SvcdbFileWk.file_type_id == file_type_id)
        return query.all()

    def addFile(self, svcdbFile, userId):
        svcdbFile.is_deleted = 0
        svcdbFile.created_at = datetime.now()
        svcdbFile.created_by = userId
        svcdbFile.updated_at = datetime.now()
        svcdbFile.updated_by = userId
        return db.session.add(svcdbFile)

    def delFile(self, edit_id, file_id, userId):
        del_file = db.session.query(SvcdbFileWk).filter(SvcdbFileWk.edit_id == edit_id,
                                                      SvcdbFileWk.file_id == file_id).first()
        del_file.is_deleted = 1
        del_file.deleted_at = datetime.now()
        del_file.deleted_by = userId

    def delFiles(self, parent_object_id, file_type_id=None):
        query = db.session.query(SvcdbFileWk).filter(SvcdbFileWk.parent_object_id == parent_object_id)
        if file_type_id != None and file_type_id > 0:
            query = query.filter(SvcdbFileWk.file_type_id == file_type_id)
        query.delete()

    def intFileDatas(self, edit_id, parent_object_id):
        mergeSql = '''
            INSERT INTO SVCDB_FILE_WK
            SELECT :edit_id EDIT_ID, FILE_ID, PARENT_OBJECT_ID, FILE_TYPE_ID, FILE_NAME, FILE_SIZE,
                   DIR_NAME, C_FILE_NAME, C_FILE_SIZE, IS_DELETED, CREATED_AT, CREATED_BY,
                   UPDATED_AT, UPDATED_BY, DELETED_AT, DELETED_BY
              FROM SVCDB_FILE
             WHERE PARENT_OBJECT_ID = :parent_object_id
               AND IS_DELETED = 0
        '''
        t = text(mergeSql)
        db.session.execute(t, {"edit_id": edit_id, "parent_object_id": parent_object_id})

    def get_file_list(self, edit_id, object_id, file_type_id=None):
        selectSql = '''
            SELECT {select_columns}
            FROM SVCDB_FILE_WK T
            WHERE T.IS_DELETED = 0
              AND T.EDIT_ID = :edit_id
              AND T.PARENT_OBJECT_ID = :object_id
        '''
        params = {}
        params['edit_id'] = edit_id
        params['object_id'] = object_id
        if file_type_id != None:
            selectSql += '              AND T.FILE_TYPE_ID = :file_type_id'
            params['file_type_id'] = file_type_id

        selectSql += '            ORDER BY T.UPDATED_AT DESC'
        selectSql = selectSql.format(select_columns=SvcdbFileWk.SELECT_COLUMN_STR)
        t = text(selectSql)
        rst = db.session.execute(t, params)
        return rst

    def get_file_list_for_json(self, edit_id, object_id, file_type_id):
        selectSql = '''
            SELECT {select_columns}
            FROM SVCDB_FILE_WK T
            WHERE T.IS_DELETED = 0
              AND T.EDIT_ID = :edit_id
              AND T.PARENT_OBJECT_ID = :object_id
        '''
        execParam = {'edit_id': edit_id, 'object_id': object_id}
        if file_type_id != None and len(file_type_id) > 0:
            selectSql += " AND T.FILE_TYPE_ID = :file_type_id"
            execParam["file_type_id"] = file_type_id

        selectSql += '            ORDER BY T.UPDATED_AT DESC'
        selectSql = selectSql.format(select_columns=SvcdbFileWk.SELECT_COLUMN_STR)
        t = text(selectSql)
        rst = db.session.execute(t, execParam)
        return rst

    def getExistsFile(self, af_obj):
        selectSql = '''
            SELECT F.*
            FROM SVCDB_FILE_WK F
            WHERE F.EDIT_ID = :edit_id
              AND F.PARENT_OBJECT_ID = :parent_object_id
              AND F.IS_DELETED = '0'
              AND F.FILE_NAME = :file_name
        '''
        execParam = {'edit_id': af_obj.edit_id,
                     'parent_object_id': af_obj.parent_object_id,
                     'file_name': af_obj.file_name}
        if af_obj.file_type_id != None:
            selectSql += " AND F.FILE_TYPE_ID = :file_type_id"
            execParam["file_type_id"] = af_obj.file_type_id

        t = text(selectSql)
        rst = db.session.execute(t, execParam).first()
        return rst

    def chkExistsFile(self, af_obj):
        svcdbFileE = SvcdbFileWk()
        file = svcdbFileE.getExistsFile(af_obj)
        if not file:
            return False

        af_obj.file_id = file.file_id
        return True
