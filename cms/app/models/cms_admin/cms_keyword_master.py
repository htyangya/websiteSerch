from sqlalchemy.sql import text

from app import db


class CmsKeywordMaster(db.Model):
    __tablename__ = 'CMS_KEYWORD_MASTER'
    keyword_id = db.Column(db.Integer, primary_key=True)
    keyword_mst_id = db.Column(db.Integer)
    keyword = db.Column(db.String(500))
    display_order = db.Column(db.Integer)

    def __init__(self, keyword=None):
        self.keyword = keyword

    def getCmsKeywordMaster(self, keyword_id):
        return db.session.query(CmsKeywordMaster).filter(CmsKeywordMaster.keyword_id == keyword_id).first()

    def getKeywords(self, keyword_mst_id):
        return db.session.query(CmsKeywordMaster).filter(CmsKeywordMaster.keyword_mst_id == keyword_mst_id).all()

    def addKeywordMaster(self, cmsKeywordMaster):
        return db.session.add(cmsKeywordMaster)

    def deleteKeywords(self, keyword_mst_id):
        deleteSql = '''
            DELETE FROM CMS_KEYWORD_MASTER T
            WHERE T.KEYWORD_MST_ID = :keyword_mst_id
            AND T.KEYWORD_ID NOT IN (
                SELECT OK.KEYWORD_ID
                FROM CMS_OBJECT_KEYWORD OK, CMS_OBJECT O
                WHERE OK.OBJECT_ID = O.OBJECT_ID
                AND O.IS_DELETED = 0
            )
        '''
        db.session.execute(text(deleteSql), {'keyword_mst_id': keyword_mst_id})

    def getKeywordList(self, keyword_mst_id):
        selectSql = '''
            SELECT T.KEYWORD_MST_ID, T.KEYWORD_ID, T.KEYWORD, T.DISPLAY_ORDER
            FROM CMS_KEYWORD_MASTER T
            WHERE T.KEYWORD_MST_ID = :keyword_mst_id
            ORDER BY T.DISPLAY_ORDER
        '''
        rst = db.session.execute(text(selectSql), {'keyword_mst_id': keyword_mst_id})

        keywordList = []
        for keyword in rst:
            keywordList.append(keyword.keyword)
        return keywordList

    def getKeywordListForJson(self, keyword_mst_id, separator, show_obj_cnt_flg=0):
        keyword_sql = 'T.KEYWORD'
        if show_obj_cnt_flg:
            keyword_sql = 'GET_OBJECT_NAME_WITH_CNT(T.KEYWORD, PKG_CMS_SEARCH_UTIL.GET_KEYWORD_OBJ_CNT(T.KEYWORD_ID)) KEYWORD'

        selectSql = f'''
            SELECT T.KEYWORD_MST_ID, T.KEYWORD_ID,
                {keyword_sql},
                T.DISPLAY_ORDER
            FROM CMS_KEYWORD_MASTER T
            WHERE T.KEYWORD_MST_ID = :keyword_mst_id
            ORDER BY T.DISPLAY_ORDER
        '''
        rst = db.session.execute(text(selectSql), {'keyword_mst_id': keyword_mst_id})

        dic, idDic, array = {}, {}, []
        index, kwLength = 0, 0
        for row in rst:
            keyword_id = row.keyword_id
            display_order = row.display_order
            keywords = row.keyword.split(separator)
            level = 1
            keyTemp = ''
            kwLength = len(keywords)
            index = 1
            for keyword in keywords:
                dic = {}
                key = str(keyword_mst_id) + '_' + str(level) + '_' + keyword
                if kwLength == index:
                    key += '_' + str(keyword_id) + '_L'

                if not (key in idDic):
                    dic = {**dic, **{'id': key}}
                    dic = {**dic, **{'keyword_id': keyword_id}}
                    if level == 1:
                        dic = {**dic, **{'parent': keyword_mst_id}}
                    else:
                        dic = {**dic, **{'parent': keyTemp}}

                    dic = {**dic, **{'disp_order': int(str(level) + str(display_order))}}
                    dic = {**dic, **{'text': keyword}}
                    dic = {**dic, **{'state': {'opened': False}}}
                    idDic[key] = dic
                    array.append(dic)

                keyTemp = key
                level += 1
                index += 1

        return array

    def getUsingKeywordList(self, keyword_mst_id):
        selectSql = '''
            SELECT KEYWORD
            FROM CMS_KEYWORD_MASTER KM
            WHERE KM.KEYWORD_ID IN (
                SELECT OK.KEYWORD_ID
                FROM CMS_OBJECT_KEYWORD OK, CMS_OBJECT O
                WHERE OK.OBJECT_ID = O.OBJECT_ID
                AND O.IS_DELETED = 0
            )
            AND KM.KEYWORD_MST_ID = :keyword_mst_id
            ORDER BY KM.KEYWORD
        '''
        rst = db.session.execute(text(selectSql), {'keyword_mst_id': keyword_mst_id})

        usingKeywordList = []
        for keyword in rst:
            usingKeywordList.append(keyword.keyword)

        return usingKeywordList

    def updateUsingKeywordDisplayOrder(self, keyword_mst_id, keyword, display_order):
        selectSql = '''
            UPDATE CMS_KEYWORD_MASTER KM
            SET KM.DISPLAY_ORDER = :display_order
            WHERE KM.KEYWORD_MST_ID = :keyword_mst_id
            AND KM.KEYWORD = :keyword
        '''
        db.session.execute(text(selectSql), {
            'keyword_mst_id': keyword_mst_id,
            'keyword': keyword,
            'display_order': display_order})
