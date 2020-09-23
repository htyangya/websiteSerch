from datetime import datetime

from sqlalchemy.sql import text

from app import db


class CmsFolder(db.Model):
    __tablename__ = 'CMS_FOLDER'
    folder_id = db.Column(db.Numeric(10), primary_key=True)
    parent_folder_id = db.Column(db.Numeric(10))
    db_id = db.Column(db.Numeric(10))
    folder_name = db.Column(db.String(100))
    display_order = db.Column(db.Numeric(10))
    information_message = db.Column(db.String(2000))
    remarks = db.Column(db.String(1000))
    is_deleted = db.Column(db.Numeric(1))
    child_object_type_id = db.Column(db.Numeric(10))
    list_format_id = db.Column(db.Numeric(10))
    property_format_id = db.Column(db.Numeric(10))
    form_format_id = db.Column(db.Numeric(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(32))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.String(32))
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.String(32))

    def __init__(self, folder_id=None, parent_folder_id=None):
        self.folder_id = folder_id
        self.parent_folder_id = parent_folder_id

    def get_id(self):
        return self.folder_id

    def getFolder(self, folder_id):
        return db.session.query(CmsFolder).filter(CmsFolder.folder_id == folder_id).first()

    def getFolderTxt(self, db_id, display_order, folder_id):
        selectSql = '''
            with p as (
                select 
                      list_collect(cast(collect(t.folder_name order by rownum desc nulls last) as varchar2_array), ' > ') as folder_path
                from (
                    select folder_id, parent_folder_id, folder_name, is_deleted
                    from cms_folder f
                    where db_id = :db_id
                    and f.parent_folder_id <> 0
                    and f.is_deleted = 0
                    start with f.folder_id = :folder_id
                    connect by prior f.parent_folder_id = f.folder_id
                ) t
            )
            select (select tab_name from cms_tree_view_setting s where db_id = :db_id and display_order = :display_order) tab_name, p.folder_path from p
            '''
        t = text(selectSql)
        return db.session.execute(t, {'db_id': db_id, 'folder_id': folder_id, 'db_id': db_id, 'display_order': display_order}).first()

    def getRootFolderId(self, db_id):
        selectSql = '''
            select F.FOLDER_ID
            from CMS_FOLDER F
            where F.IS_DELETED = 0
              and F.DB_ID = :db_id
              and F.PARENT_FOLDER_ID = 0
            '''
        t = text(selectSql)
        rst = db.session.execute(t, {'db_id': db_id}).first()
        if (rst is not None):
            return rst.folder_id
        return ""

    def getFolderListForJson(self, db_id, pf_id, show_obj_cnt_flg=0):
        folder_sql = 'F.FOLDER_NAME TEXT'
        if show_obj_cnt_flg:
            folder_sql = 'GET_OBJECT_NAME_WITH_CNT(F.FOLDER_NAME, PKG_CMS_SEARCH_UTIL.GET_FOLDER_OBJ_CNT(F.FOLDER_ID)) TEXT'
        selectSql = f'''
            select F.FOLDER_ID || '_' || F.LIST_FORMAT_ID ID,
                   {folder_sql},
                   (select COUNT(1) from CMS_FOLDER F2 where F2.IS_DELETED = 0 and F2.PARENT_FOLDER_ID = F.FOLDER_ID) CHILDREN,
                   F.CHILD_OBJECT_TYPE_ID, F.DISPLAY_ORDER DISP_ORDER
            from CMS_FOLDER F
            where F.IS_DELETED = 0
              and F.DB_ID = :db_id
              and F.PARENT_FOLDER_ID = :pf_id
            order by F.DISPLAY_ORDER
            '''
        t = text(selectSql)
        resultproxy = db.session.execute(
            t, {'db_id': db_id, 'pf_id': pf_id})

        dic, array = {}, []
        for rowproxy in resultproxy:
            dic = {}
            for column, val in rowproxy.items():
                value = ""
                if (column == 'children'):
                    if (val > 0):
                        value = True
                    else:
                        value = False
                else:
                    value = val
                dic = {**dic, **{column: value}}
            array.append(dic)

        return array

    # インフォメーションメッセージを取得
    def getInformationMessage(self, folder_id):
        selectSql = '''
            SELECT * FROM CMS_FOLDER F
            WHERE F.FOLDER_ID = :folder_id
        '''
        t = text(selectSql)
        rst = db.session.execute(t, {'folder_id': folder_id}).first()
        if (rst is not None):
            return rst.information_message
        return ""
