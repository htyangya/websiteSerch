from sqlalchemy.sql import text

from app import db


class CmsTreeViewSetting(db.Model):
    __tablename__ = 'CMS_TREE_VIEW_SETTING'
    db_id = db.Column(db.Integer, primary_key=True)
    display_order = db.Column(db.Integer, primary_key=True)
    view_type = db.Column(db.String(20))
    tab_name = db.Column(db.String(100))
    keyword_mst_id = db.Column(db.Integer)
    tree_open_flg = db.Column(db.Integer)

    def __init__(self, db_id=None):
        self.db_id = db_id

    def getTreeViewSetting(self, db_id, view_type):
        return db.session.query(CmsTreeViewSetting) \
            .filter(CmsTreeViewSetting.db_id == db_id, CmsTreeViewSetting.view_type == view_type).first()

    def getTreeViewSettingList(self, db_id):
        selectSql = '''
       SELECT T.DB_ID, T.DISPLAY_ORDER, T.VIEW_TYPE, T.TAB_NAME, 
              T.KEYWORD_MST_ID, T.TREE_OPEN_FLG
         FROM CMS_TREE_VIEW_SETTING T
        WHERE T.DB_ID = :db_id
        ORDER BY T.DISPLAY_ORDER
        '''
        t = text(selectSql)
        rst = db.session.execute(t, {'db_id': db_id})
        return rst
