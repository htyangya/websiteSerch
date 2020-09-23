from app import db


class CmsSearchSetting(db.Model):
    __tablename__ = 'CMS_SEARCH_SETTING'
    search_setting_id = db.Column(db.Integer, primary_key=True)
    db_id = db.Column(db.Integer)
    object_type_id = db.Column(db.Integer)
    search_menu_title = db.Column(db.String(200))
    search_dlg_format_id = db.Column(db.Integer)
    result_format_id = db.Column(db.Integer)

    def getSearchSetting(self, search_setting_id):
        return db.session.query(CmsSearchSetting) \
            .filter(CmsSearchSetting.search_setting_id == search_setting_id).first()

    def getSearchSettingByDbId(self, db_id):
        return db.session.query(CmsSearchSetting) \
            .filter(CmsSearchSetting.db_id == db_id).first()