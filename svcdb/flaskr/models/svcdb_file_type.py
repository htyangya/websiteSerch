from flaskr import db


class SvcdbFileType(db.Model):
    __tablename__ = 'SVCDB_FILE_TYPE'

    file_type_id = db.Column(db.Integer, primary_key=True)
    file_type_name = db.Column(db.String(100))
    object_type_id = db.Column(db.Integer)
    open_flg = db.Column(db.Integer)
    ctx_flg = db.Column(db.Integer)
    max_file_cnt = db.Column(db.Integer)
    display_order = db.Column(db.Integer)
    remarks = db.Column(db.String(2000))
    ctx_title_format = db.Column(db.String(200))
    log_notes_format = db.Column(db.String(200))

    def __init__(self, file_type_name=None):
        self.file_type_name = file_type_name

    def getFileTypeList(self, object_type_id, func=None):
        if func and func == 'show_property':
            return db.session.query(SvcdbFileType).filter(
                SvcdbFileType.object_type_id == object_type_id,
                SvcdbFileType.open_flg == 1).all()
        return db.session.query(SvcdbFileType).filter(SvcdbFileType.object_type_id == object_type_id).all()

    def getFileTypeInfo(self, file_type_id):
        return db.session.query(SvcdbFileType).filter(SvcdbFileType.file_type_id == file_type_id).first()
