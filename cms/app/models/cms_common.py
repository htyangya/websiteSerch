from app import db


class CmsCommon():
    def getObjectIdSeq(self):
        self.seqId = db.session.execute(
            'select object_id_sequence.nextval as seq_id from dual').fetchone().seq_id
        return self.seqId
