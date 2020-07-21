from app import db


class CmsCommon():
    def getObjectIdSeq(self):
        self.seqId = db.session.execute(
            'select object_id_sequence.nextval as seq_id from dual').fetchone().seq_id
        return self.seqId

    @staticmethod
    def getObjectIdSeqList(count):
        objs = db.session.execute(
            f"select object_id_sequence.nextval oid from dual connect  by level <= {count}"
        ).fetchall()
        return [obj.oid for obj in objs]
