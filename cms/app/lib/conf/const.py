class Const(object):
    DEVELOPMENT = 'DEVELOPMENT'
    PRODUCTION = 'PRODUCTION'
    FILE_ALLOWED_EXTENSIONS = ['xls', 'xlsx', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
    # 処理可能な種類
    CTX_FILE_ALLOWED_EXTENSIONS = ['pdf']
    # VIEW_TYPE
    FOLDER = "FOLDER"
    KEYWORD = "KEYWORD"

    URL_FORMAT = '{}?{}'
    NO_FILE_FOUND_MSG = 'File not found: {}'
    UNZIP_ERROR_MSG = 'File not unzip: {}'
    CMD_ERROR_MSG = 'Extract text error: {}'
    CONTACT_FORMAT = '{}\n{}'
    FILE_EXTENSION_FORMAT = '{}.{}'
    DEBUG_MSG_FORMAT = '【DEBUG INFO: {}】'
    ERROR_MSG_FORMAT = '【ERROR INFO: {}】'
    DATA_TYPE_OBJECT = 'OBJECT'
    DATA_TYPE_FILE = 'FILE'
    DATE_FORMAT = 'YYYY/MM/DD'

    # 操作ログ
    OPERATION_CD_LOGIN = 'LOGIN'
    OPERATION_CD_CREATE_OBJECT = 'CREATE_OBJECT'
    OPERATION_CD_UPDATE_OBJECT = 'UPDATE_OBJECT'
    OPERATION_CD_DELETE_OBJECT = 'DELETE_OBJECT'
    OPERATION_CD_CREATE_FILE = 'CREATE_FILE'
    OPERATION_CD_DELETE_FILE = 'DELETE_FILE'
    OPERATION_CD_SHOW_FILE = 'SHOW_FILE'
    OPERATION_CD_CTX_SEARCH = 'CTX_SEARCH'
    OPERATION_CD_ADD_PRIVS_USER = 'ADD_PRIVS_USER'
    OPERATION_CD_UPDATE_PRIVS_USER = 'UPDATE_PRIVS_USER'
    OPERATION_CD_DELETE_PRIVS_USER = 'DELETE_PRIVS_USER'
    OPERATION_CD_CORP_SEARCH = 'CORP_SEARCH'
    OPERATION_CD_ADD_PRIVS_DEPT = 'ADD_PRIVS_DEPT'
    OPERATION_CD_UPDATE_PRIVS_DEPT = 'UPDATE_PRIVS_DEPT'
    OPERATION_CD_DELETE_PRIVS_DEPT = 'DELETE_PRIVS_DEPT'

    # ユーザー操作
    ADD_PRIVS_USER = 'ADD_PRIVS_USER'
    UPDATE_PRIVS_USER = 'UPDATE_PRIVS_USER'
    DELETE_PRIVS_USER = 'DELETE_PRIVS_USER'

    PRIVS_USER_TITLE = {
        ADD_PRIVS_USER: 'Add Privs User',
        UPDATE_PRIVS_USER: 'Update Privs User',
        DELETE_PRIVS_USER: 'Delete Privs User',
    }

    ADD_PRIVS_DEPT = 'ADD_PRIVS_DEPT'
    UPDATE_PRIVS_DEPT = 'UPDATE_PRIVS_DEPT'
    DELETE_PRIVS_DEPT = 'DELETE_PRIVS_DEPT'

    PRIVS_DEPT_TITLE = {
        ADD_PRIVS_DEPT: 'Add Privs Dept',
        UPDATE_PRIVS_DEPT: 'Update Privs Dept',
        DELETE_PRIVS_DEPT: 'Delete Privs Dept',
    }

    # エラーコード
    LOGIN_ERROR = 'LOGIN_ERROR'
    DB_PRIVS_ERROR = 'DB_PRIVS_ERROR'
    IP_ADDRESS_ERROR = 'IP_ADDRESS_ERROR'

    # SQL用
    START = '_start'
    END = '_end'

    # STYLE_TYPE
    STYLE_TYPE_COLOR = 'COLOR'

    # ファイル
    FILE_SUFFIX_CSV = ".csv"
    FILE_SUFFIX_EXCEL = ".xlsx"
    # メッセージ
    WAIT_MSG = 'しばらくお待ちください'
    REQUIRED_MSG = '{}を指定してください'
    LENGTH_OVER_MSG = '{}に{}バイト以内指定してください'
    NUMERICAL_VALUE_REQUIRED_MSG = '{}には数字を入力してください'
    INTEGRAL_PART_OUT_OF_RANGE_MSG = '{}の整数部分は{}桁以下に入力してください'
    FRACTIONAL_PART_OUT_OF_RANGE_MSG = '{}の小数部分は{}桁以下に入力してください'
    INTEGER_VALUE_REQUIRED_MSG = '{}には整数を入力してください'
    AVAILABLE_DATE_REQUIRED_MSG = '{}には正確な日付を入力してください({})'
    NOT_FILE_ALLOWED_MSG = '「{}」をアップロードできません。'
    SELECT_CORP_MSG = '対象の組織を選択してください'
    ZERO_LIST_MSG = '検索結果は0件です'
    INVALID_PARAM_ERR_MSG = '引数が無効です'
    CANNOT_DELETE_USING_ITEM_ERR_MSG = '「{}」は使用中のため削除できません'
    IP_ADDRESS_OVERLAP_ERR_MSG = 'IP Addressが既に存在しています。'

    SEARCH_USER_REQUIRED_ERR_MSG = 'Search user is required.'
    DATA_EXIST_ERR_MSG = 'Data is exist.'
    USER_ID_NOT_EXIST_ERR_MSG = 'User Id　is not exist.'
    USER_ID_ERR_MSG = 'User Id is required.'
    USER_NAME_ERR_MSG = 'User Name is required.'

    DATA_NOT_EXIST_ERR_MSG = '%s is not exist.'
    DATA_REQUIRED_ERR_MSG = '%s is required.'
    CORP_NOT_EXIST_ERR_MSG = 'Corp Cd is not exist.'
    CORP_CD_ERR_MSG = 'Corp Cd is required.'
    DIV_CD_ERR_MSG = 'Div Cd is required.'
    DEPT_CD_ERR_MSG = 'Dept Cd is required.'

    IP_ADDRESS_SAVE_ERROR = 'IP Address save failed.'

    # BATCH FILE UPLOAD
    EXCEL_FILE_NOT_FOUND_MSG = "Please drop or select an excel file."
    NOT_XLSX_FILE_MSG = "Xlsx(excel) file is required."

    SELECTION_MST_DELETE_MSG = "Are you sure delete this selection master?"
    SELECTION_DATA_DELETE_MSG = "Are you sure delete this selection data?"
    SELECTION_MST_CAN_NOT_DELETE_MSG = "Can not delete this selection master."
    SELECTION_DATA_CAN_NOT_DELETE_MSG = "Can not delete this selection data."
