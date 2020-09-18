from datetime import datetime
from flask_login import current_user
from app import db


class CmsObjectPropSelectionList(db.Model):
    __tablename__ = 'CMS_OBJECT_PROP_SELECTION_LIST'
    selection_id = db.Column(db.Integer, primary_key=True)
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
