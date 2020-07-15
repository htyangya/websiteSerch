from app import db


class CmsObjectPropSelectionMst(db.Model):
    __tablename__ = 'CMS_OBJECT_PROP_SELECTION_MST'

    selection_mst_id = db.Column(db.Integer, primary_key=True)
    db_id = db.Column(db.Integer)
    selection_mst_name = db.Column(db.String(200))
    parent_selection_mst_id = db.Column(db.Integer)
    remarks = db.Column(db.String(1000))
    display_order = db.Column(db.Integer)

    def getObjectPropSelectionMst(self, selection_mst_id):
        return db.session.query(CmsObjectPropSelectionMst) \
            .filter(CmsObjectPropSelectionMst.selection_mst_id == selection_mst_id).first()
