from sqlalchemy.sql import text

from app import db


class CmsKeywordSetting(db.Model):
    __tablename__ = 'CMS_KEYWORD_SETTING'
    keyword_mst_id = db.Column(db.Integer, primary_key=True)
    db_id = db.Column(db.Integer)
    keyword_name = db.Column(db.String(100))
    multi_set_flg = db.Column(db.Integer)
    multiSetFlg = ''
    not_null_flg = db.Column(db.Integer)
    notNullFlg = ''
    tree_separator = db.Column(db.String(10))
    format_id = db.Column(db.Integer)
    keywords = []

    def __init__(self, keyword_name=None):
        self.keyword_name = keyword_name

    def setKeywords(self, keywords=None):
        self.keywords = keywords

    def getCmsKeywordSetting(self, keyword_mst_id):
        return db.session.query(CmsKeywordSetting).filter(CmsKeywordSetting.keyword_mst_id == keyword_mst_id).first()

    def addKeywordSetting(self, cmsKeywordSetting):
        return db.session.add(cmsKeywordSetting)

    def getKeywordSettingList(self, db_id, keyword_mst_id=None):
        selectSql = '''
            SELECT T.KEYWORD_MST_ID, T.DB_ID, T.KEYWORD_NAME, T.MULTI_SET_FLG, T.NOT_NULL_FLG, T.TREE_SEPARATOR,
                   (select COUNT(1) from CMS_KEYWORD_MASTER KM where KM.KEYWORD_MST_ID = T.KEYWORD_MST_ID) CHILDREN
            FROM CMS_KEYWORD_SETTING T
            WHERE T.DB_ID = :db_id
        '''
        exec_args = {'db_id': db_id}
        if keyword_mst_id is not None and len(keyword_mst_id) > 0:
            selectSql += '          AND T.KEYWORD_MST_ID = :keyword_mst_id'
            exec_args['keyword_mst_id'] = keyword_mst_id

        rst = db.session.execute(text(selectSql), exec_args)
        return rst

    def getKeywordSettingListForJson(self, db_id, keyword_mst_id=None):
        cmsKeywordSetting = CmsKeywordSetting()
        rst = cmsKeywordSetting.getKeywordSettingList(db_id, keyword_mst_id)

        dic, array = {}, []
        for row in rst:
            dic = {**dic, **{'id': str(row.keyword_mst_id)}}
            dic = {**dic, **{'parent': '#'}}
            dic = {**dic, **{'text': row.keyword_name}}
            dic = {**dic, **{'separator': row.tree_separator}}
            array.append(dic)

        return array

    def getCmsKeywordSettingByKeywordId(self, db_id, keyword_id):
        selectSql = '''
                SELECT T.KEYWORD_MST_ID, T.DB_ID, T.KEYWORD_NAME, T.MULTI_SET_FLG, T.NOT_NULL_FLG, T.TREE_SEPARATOR, T.FORMAT_ID
                FROM CMS_KEYWORD_SETTING T, CMS_KEYWORD_MASTER KM
                WHERE T.DB_ID = :db_id
                  AND T.KEYWORD_MST_ID = KM.KEYWORD_MST_ID
                  AND KM.KEYWORD_ID = :keyword_id
                '''
        rst = db.session.execute(text(selectSql), {'db_id': db_id, 'keyword_id': keyword_id}).first()
        return rst
