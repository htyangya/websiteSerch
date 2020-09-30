from datetime import datetime
from flask_login import current_user
from sqlalchemy import Sequence

from app import db
from app.models.cms_db_admin.cms_object_property import CmsObjectProperty


class CmsObjectPropSelectionList(db.Model):
    __tablename__ = 'CMS_OBJECT_PROP_SELECTION_LIST'
    id_seq = Sequence('OBJECT_ID_SEQUENCE')
    selection_id = db.Column(db.Integer, id_seq,
                             server_default=id_seq.next_value(), primary_key=True)
    selection_mst_id = db.Column(db.Integer)
    selection_name = db.Column(db.String(400))
    parent_selection_id = db.Column(db.Integer)
    description = db.Column(db.String(1000))
    display_order = db.Column(db.Integer)
    is_deleted = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    created_by = db.Column(db.String(), default=lambda: current_user.get_id())
    updated_at = db.Column(db.DateTime, default=datetime.now)
    updated_by = db.Column(db.String(), default=lambda: current_user.get_id())
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.String)

    def getObjectPropSelectionList(self, selection_mst_id):
        return db.session.query(CmsObjectPropSelectionList) \
            .filter(CmsObjectPropSelectionList.selection_mst_id == selection_mst_id,
                    CmsObjectPropSelectionList.is_deleted == 0) \
            .order_by(CmsObjectPropSelectionList.display_order).all()

    def getSelectionMstDic(self, proList):
        selection_mst_dic, selection_list, selection_dic = {}, [], {}
        for pro in proList:
            if 'SELECT' == pro.get('property_type'):
                selection_mst_id = pro.get("selection_mst_id")
                if not selection_mst_id in selection_mst_dic:
                    selList = CmsObjectPropSelectionList().getObjectPropSelectionList(selection_mst_id)
                    if len(selList) > 0:
                        for sel in selList:
                            selection_dic = {}
                            selection_dic["value"] = sel.selection_id
                            selection_dic["label"] = sel.selection_name
                            selection_list.append(selection_dic)

                    selection_mst_dic[selection_mst_id] = selection_list
        return selection_mst_dic

    def _get_can_delete(self):
        str_template = "{0} = %s" % self.selection_id
        db_column_obj = CmsObjectProperty.query.filter(CmsObjectProperty.property_type == "SELECT",
                                                       CmsObjectProperty.db_column_name.isnot(None)).with_entities(
            CmsObjectProperty.db_column_name).all()
        sql_str = " OR ".join(map(lambda obj: str_template.format(obj[0]), db_column_obj))
        sql_str = "SELECT COUNT(*) FROM CMS_OBJECT WHERE " + sql_str
        return not db.session.execute(sql_str).scalar()

    @property
    def can_delete(self):
        if not hasattr(self, "_can_delete"):
            self._can_delete = self._get_can_delete()
        return self._can_delete
