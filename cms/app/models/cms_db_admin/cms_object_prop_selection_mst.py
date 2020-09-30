from datetime import datetime

from flask_login import current_user
from sqlalchemy import Sequence

from app import db
from app.models.cms_db_admin.cms_object_property import CmsObjectProperty


class CmsObjectPropSelectionMst(db.Model):
    __tablename__ = 'CMS_OBJECT_PROP_SELECTION_MST'
    id_seq = Sequence('OBJECT_ID_SEQUENCE')
    selection_mst_id = db.Column(db.Integer, id_seq,
                                 server_default=id_seq.next_value(), primary_key=True)
    db_id = db.Column(db.Integer)
    selection_mst_name = db.Column(db.String(200))
    parent_selection_mst_id = db.Column(db.Integer)
    remarks = db.Column(db.String(1000))
    display_order = db.Column(db.Integer)
    is_deleted = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    created_by = db.Column(db.String(), default=lambda: current_user.get_id())
    updated_at = db.Column(db.DateTime, default=datetime.now)
    updated_by = db.Column(db.String(), default=lambda: current_user.get_id())
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.String)

    def getObjectPropSelectionMst(self, selection_mst_id):
        return db.session.query(CmsObjectPropSelectionMst) \
            .filter(CmsObjectPropSelectionMst.selection_mst_id == selection_mst_id).first()

    @property
    def can_delete(self):
        if not hasattr(self, "_can_delete"):
            self._can_delete = not CmsObjectProperty.query.filter(
                CmsObjectProperty.selection_mst_id == self.selection_mst_id).count()
        return self._can_delete
