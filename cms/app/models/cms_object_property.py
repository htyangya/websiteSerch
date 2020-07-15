from sqlalchemy.sql import text

from app import db


class CmsObjectProperty():
    __tablename__ = 'CMS_OBJECT_PROPERTY'
    property_id = db.Column(db.Numeric(10), primary_key=True)
    object_type_id = db.Column(db.Numeric(10))
    property_name = db.Column(db.String(100))
    db_column_name = db.Column(db.String(30))
    property_type = db.Column(db.String(20))
    property_name_req = db.Column(db.String(10))
    data_size = db.Column(db.Numeric(4))
    i_len = db.Column(db.Numeric(4))
    f_len = db.Column(db.Numeric(4))
    selection_mst_id = db.Column(db.Numeric(10))
    parent_property_id = db.Column(db.Numeric(10))
    validate_rule = db.Column(db.String(100))
    validate_err_msg = db.Column(db.String(1000))
    display_order = db.Column(db.Integer)
    remarks = db.Column(db.String(2000))
    keyword_mst_id = db.Column(db.Numeric(10))

    def getObjectPropertiesByFormatId(self, format_id):
        selectSql = '''
              SELECT
                  FMT_COL.FORMAT_ID
                 ,FMT_COL.DISPLAY_ORDER COL_ORDER
                 ,FMT_COL.PROPERTY_ID
                 ,FMT_COL.LINK_TYPE
                 ,FMT_COL.LINK_TYPE_ID
                 ,FMT_COL.TD_STYLE
                 ,FMT_COL.LINK_FORMAT
                 ,OBJ_PTY.PROPERTY_NAME
                 ,OBJ_PTY.PROPERTY_TYPE
                 ,OBJ_PTY.NULLABLE
                 ,CASE WHEN OBJ_PTY.NULLABLE = 'FALSE' THEN ' (*) ' ELSE '' END PROPERTY_NAME_REQ
                 ,OBJ_PTY.DB_COLUMN_NAME
                 ,OBJ_PTY.DATA_SIZE
                 ,OBJ_PTY.I_LEN
                 ,OBJ_PTY.F_LEN
                 ,OBJ_PTY.SELECTION_MST_ID
                 ,OBJ_PTY.PARENT_PROPERTY_ID
                 ,OBJ_PTY.VALIDATE_RULE
                 ,OBJ_PTY.VALIDATE_ERR_MSG
                 ,OBJ_PTY.REMARKS
                 ,OBJ_PTY.KEYWORD_MST_ID
                 ,FMT_SORT.DISPLAY_ORDER LIST_ORDER
                 ,FMT_SORT.SORT_KEY_ORDER
              FROM CMS_OBJECT_PROPERTY OBJ_PTY
             INNER JOIN CMS_LIST_FORMAT_COLUMNS FMT_COL
                     ON FMT_COL.PROPERTY_ID = OBJ_PTY.PROPERTY_ID
              LEFT JOIN CMS_LIST_FORMAT_SORT FMT_SORT
                     ON FMT_COL.FORMAT_ID = FMT_SORT.FORMAT_ID
                    AND FMT_COL.PROPERTY_ID = FMT_SORT.PROPERTY_ID
             WHERE FMT_COL.FORMAT_ID = :format_id
          ORDER BY FMT_COL.DISPLAY_ORDER
        '''
        t = text(selectSql)
        rst = db.session.execute(t, {'format_id': format_id})

        dic, array = {}, []
        for rowproxy in rst:
            for column, val in rowproxy.items():
                dic = {**dic, **{column: val}}
            array.append(dic)

        return array

    def getObjectSortPropertiesByFormatId(self, format_id):
        selectSql = '''
              SELECT FMT_SORT.FORMAT_ID,
                     FMT_SORT.DISPLAY_ORDER,
                     FMT_SORT.PROPERTY_ID,
                     FMT_SORT.SORT_KEY_ORDER,
                     OBJ_PTY.DB_COLUMN_NAME,
                     OBJ_PTY.PROPERTY_TYPE
              FROM CMS_LIST_FORMAT_SORT FMT_SORT, CMS_OBJECT_PROPERTY OBJ_PTY
             WHERE FMT_SORT.FORMAT_ID = :format_id
               AND FMT_SORT.PROPERTY_ID = OBJ_PTY.PROPERTY_ID
             ORDER BY FMT_SORT.DISPLAY_ORDER
        '''
        t = text(selectSql)
        rst = db.session.execute(t, {'format_id': format_id})
        dic, array = {}, []
        for rowproxy in rst:
            for column, val in rowproxy.items():
                dic = {**dic, **{column: val}}
            array.append(dic)

        return array

    def getCtxObjectDbNames(self, object_type_id):
        selectSql = '''
            SELECT COP.PROPERTY_ID,
                   COP.DB_COLUMN_NAME
              FROM CMS_OBJECT_PROPERTY COP
             WHERE COP.OBJECT_TYPE_ID = :object_type_id
               AND COP.CTX_FLG = 1
             ORDER BY COP.DISPLAY_ORDER
        '''
        t = text(selectSql)
        return db.session.execute(t, {'object_type_id': object_type_id})

    def getObjectPropertyNames(self, object_type_id):
        selectSql = '''
            SELECT COP.PROPERTY_ID,
                   COP.PROPERTY_NAME,
                   COP.PROPERTY_TYPE
              FROM CMS_OBJECT_PROPERTY COP
             WHERE COP.OBJECT_TYPE_ID = :object_type_id
               
             ORDER BY COP.DISPLAY_ORDER
        '''
        t = text(selectSql)
        return db.session.execute(t, {'object_type_id': object_type_id})
