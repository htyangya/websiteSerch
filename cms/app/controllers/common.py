from flask import jsonify

from app import db


class Common():
    def error_handler(error):
        response = jsonify({
            "error": {
                "type": "error.args",
                "message": "error.with_traceback(sys.exc_info()[2])"
            }
        })
        return response


class CreateSeq():
    @staticmethod
    def getSessionIdSeq():
        seqId = db.session.execute(
            'select session_id_sequence.nextval as seq_id from dual').fetchone().seq_id
        return seqId
