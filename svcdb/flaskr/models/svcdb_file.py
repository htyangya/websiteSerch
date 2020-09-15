from datetime import datetime

from sqlalchemy.sql import text

from flaskr import db


class SvcdbFile(db.Model):
    __tablename__ = 'SVCDB_FILE'

    file_id = db.Column(db.Integer, primary_key=True)
    parent_object_id = db.Column(db.Integer, index=True)
    file_type_id = db.Column(db.Integer)
    file_name = db.Column(db.String(400))
    file_size = db.Column(db.Integer)
    dir_name = db.Column(db.String(255))
    c_file_name = db.Column(db.String(20))
    c_file_size = db.Column(db.Integer)
    is_deleted = db.Column(db.Integer)
    ctx_indexed_flg = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(32))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.String(32))
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.String(32))

    SELECT_COLUMN_STR = '''
        FILE_ID, PARENT_OBJECT_ID, FILE_TYPE_ID, FILE_NAME,
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
        self.ctx_indexed_flg = 0

    def __repr__(self):
        return '<Name %r>' % (self.file_name)

    def setFileIdSeq(self, file_id):
        self.file_id = file_id

    def setUpdateInfo(self, update_by):
        self.update_by = update_by
        self.updated_at = datetime.now()

    def setCreateInfo(self, created_by):
        self.created_by = created_by
        self.created_at = datetime.now()

    def setDeleteInfo(self, deleted_by):
        self.deleted_by = deleted_by
        self.deleted_at = datetime.now()

    def setCtxIndexedFlg(self, file_id, ctx_indexed_flg):
        updFile = db.session.query(SvcdbFile).filter(
            SvcdbFile.file_id == file_id,
            SvcdbFile.is_deleted == 0).first()
        updFile.ctx_indexed_flg = ctx_indexed_flg

    def getFile(self, file_id):
        return db.session.query(SvcdbFile).filter(SvcdbFile.file_id == file_id).first()

    def getFileList(self, parent_object_id, file_type_id):
        return db.session.query(SvcdbFile).filter(
            SvcdbFile.parent_object_id == parent_object_id,
            SvcdbFile.file_type_id == file_type_id,
            SvcdbFile.is_deleted == 0).all()

    def addFile(self, svcdbFile):
        return db.session.add(svcdbFile)

    def delFile(self, fileId, userId):
        del_file = db.session.query(SvcdbFile).filter(SvcdbFile.file_id == fileId).first()
        del_file.is_deleted = 1
        del_file.deleted_at = datetime.now()
        del_file.deleted_by = userId

    def delFiles(self, parent_object_id, userId):
        del_file_list = db.session.query(SvcdbFile).filter(SvcdbFile.parent_object_id == parent_object_id).all()
        if del_file_list != None and len(del_file_list) > 0:
            for del_file in del_file_list:
                del_file.is_deleted = 1
                del_file.deleted_at = datetime.now()
                del_file.deleted_by = userId

    def get_file_list(self, object_id, file_type_id=None):
        selectSql = '''
            SELECT {select_columns}
            FROM SVCDB_FILE T
            WHERE T.IS_DELETED = 0
              AND T.PARENT_OBJECT_ID = :object_id
        '''
        params = {}
        params['object_id'] = object_id
        if file_type_id is not None:
            selectSql += '              AND T.FILE_TYPE_ID = :file_type_id'
            params['file_type_id'] = file_type_id

        selectSql += '            ORDER BY T.UPDATED_AT DESC'
        selectSql = selectSql.format(select_columns=SvcdbFile.SELECT_COLUMN_STR)
        t = text(selectSql)
        rst = db.session.execute(t, params)
        return rst

    def get_file_list_for_json(self, object_id, file_type_id):
        selectSql = '''
            SELECT {select_columns}
            FROM SVCDB_FILE T
            WHERE T.IS_DELETED = 0
              AND T.PARENT_OBJECT_ID = :object_id
        '''
        execParam = {'object_id': object_id}
        if file_type_id is not None and len(file_type_id) > 0:
            selectSql += " AND T.FILE_TYPE_ID = :file_type_id"
            execParam["file_type_id"] = file_type_id

        selectSql = selectSql.format(select_columns=SvcdbFile.SELECT_COLUMN_STR)
        t = text(selectSql)
        rst = db.session.execute(t, execParam)
        return rst

    def get_ctx_file_list(self, object_id, file_type_id=None):
        selectSql = '''
            SELECT {select_columns}
            FROM SVCDB_FILE T
            WHERE T.IS_DELETED = 0
            AND T.CTX_INDEXED_FLG = 0
            AND T.PARENT_OBJECT_ID = :object_id
        '''
        params = {}
        params['object_id'] = object_id
        if file_type_id is not None:
            selectSql += '              AND T.FILE_TYPE_ID = :file_type_id'
            params['file_type_id'] = file_type_id
        else:
            selectSql += """
                AND T.FILE_TYPE_ID IN (
                    SELECT FT.FILE_TYPE_ID
                    FROM SVCDB_FILE_TYPE FT
                    WHERE FT.OBJECT_TYPE_ID IN (
                        SELECT O.OBJECT_TYPE_ID
                        FROM SVCDB_OBJECT O
                        WHERE O.IS_DELETED = 0
                        AND O.CTX_INDEXED_FLG = 0
                        AND O.OBJECT_ID = T.PARENT_OBJECT_ID
                    )
                    AND FT.CTX_FLG = 1
                )
            """

        selectSql += '            ORDER BY T.UPDATED_AT DESC'
        selectSql = selectSql.format(select_columns=SvcdbFile.SELECT_COLUMN_STR)
        t = text(selectSql)
        rst = db.session.execute(t, params)
        return rst

    def getExistsFile(self, af_obj):
        selectSql = '''
            SELECT F.*
            FROM SVCDB_FILE F
            WHERE F.PARENT_OBJECT_ID = :parent_object_id
              AND F.IS_DELETED = '0'
              AND F.FILE_NAME = :file_name
        '''
        execParam = {'parent_object_id': af_obj.parent_object_id,
                     'file_name': af_obj.file_name}
        if af_obj.file_type_id is not None:
            selectSql += " AND F.FILE_TYPE_ID = :file_type_id"
            execParam["file_type_id"] = af_obj.file_type_id

        t = text(selectSql)
        rst = db.session.execute(t, execParam).first()
        return rst

    def chkExistsFile(self, af_obj):
        svcdbFileE = SvcdbFile()
        file = svcdbFileE.getExistsFile(af_obj)
        if not file:
            return False

        af_obj.file_id = file.file_id
        return True
