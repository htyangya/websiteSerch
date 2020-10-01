class Const(object):
    SYSTEM_NAME = '定検ＤＢ'
    DEVELOPMENT = 'DEVELOPMENT'
    PRODUCTION = 'PRODUCTION'
    SESSION_COOKIE_NAME = "svcdb_cookie"
    FILE_ALLOWED_EXTENSIONS = ['xls', 'xlsx', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
    # 処理可能な種類
    CTX_FILE_ALLOWED_EXTENSIONS = ['pdf']

    # サブメニュー
    OUTAGE_SCHEDULE = 'outage_schedule'
    PLANT_DATA_BASE = 'Plant_Data_Base'
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
    HTML_FORMAT = 'HTML'
    TEXT_FORMAT = 'TEXT'

    # 操作ログ
    OPERATION_CD_LOGIN = 'LOGIN'
    OPERATION_CD_CREATE_OBJECT = 'CREATE_OBJECT'
    OPERATION_CD_UPDATE_OBJECT = 'UPDATE_OBJECT'
    OPERATION_CD_DELETE_OBJECT = 'DELETE_OBJECT'
    OPERATION_CD_CREATE_FILE = 'CREATE_FILE'
    OPERATION_CD_DELETE_FILE = 'DELETE_FILE'
    OPERATION_CD_SHOW_FILE = 'SHOW_FILE'
    OPERATION_CD_CTX_SEARCH = 'CTX_SEARCH'

    # メッセージ
    REQUIRED_MSG = '{}を指定してください'
    LENGTH_OVER_MSG = '{}に{}バイト以内指定してください'
    NUMERICAL_VALUE_REQUIRED_MSG = '{}には数字を入力してください'
    INTEGRAL_PART_OUT_OF_RANGE_MSG = '{}の整数部分は{}桁以下に入力してください'
    FRACTIONAL_PART_OUT_OF_RANGE_MSG = '{}の小数部分は{}桁以下に入力してください'
    INTEGER_VALUE_REQUIRED_MSG = '{}には整数を入力してください'
    AVAILABLE_DATE_REQUIRED_MSG = '{}には正確な日付を入力してください({})'

    INVALID_PARAM_ERR_MSG = '引数が無効です'
    CANNOT_DELETE_USING_ITEM_ERR_MSG = '「{}」は使用中のため削除できません'

    DATE_FORMAT_ERR_MSG = '日付エラー'
    DATE_VALUE_ERR_MSG = '終了日は開始日より後の日付を指定してください'
    TURBINE_URL_ERR_MSG = 'Error: You are not registered in Plant Data Base'
