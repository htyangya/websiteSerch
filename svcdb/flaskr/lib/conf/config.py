import os
from datetime import datetime, timedelta

from flaskr.lib.conf.const import Const


class Config:
    # Flask
    DEBUG = True

    # 環境設定
    PROJECT_STAGE = os.environ.get('PROJECT_STAGE', Const.DEVELOPMENT)
    # システムＵＲＬ
    SVCDB_SYS_URL = 'http://dev1.tsurumi.toshiba.co.jp:16480/svcdb'
    # システムクッキー
    SVCDB_SYS_COOKIE = 'svcdb_admin'
    # アプリバージョン
    APP_VER = datetime.now().strftime('%Y%m%d_%H%M')
    # 日時フォーマット
    DATE_TIME_FORMAT = 'yyyy/MM/dd HH24:mi:ss'
    PY_DATE_TIME_FORMAT = '%Y/%m/%d %H:%M:%S'
    # 日付フォーマット
    DATE_FORMAT = 'yyyy/MM/dd'
    PY_DATE_FORMAT = '%Y/%m/%d'
    # ローカルテスト用（リリース対象外）
    LOCAL_REMOTE_ADDR = '10.41.172.189'
    # 文字コード
    os.environ['NLS_LANG'] = 'JAPANESE_JAPAN.AL32UTF8'
    # ファイルアップロードサイズ制限
    # MAX_CONTENT_LENGTH = 1 * 1024 * 1024
    # ページング件数デフォルト100件
    PAGE_RANGE = 100
    # 1ページに表示する最大ページングリンク数
    MAX_PAGE_SIZE = 10

    # 「Remember me」機能対応
    REMEMBER_COOKIE_DURATION = timedelta(minutes=60)
    # デフォルトのセッションの有効期間
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'oracle+cx_oracle://{user}:{password}@{host}'.format(**{
        'user': os.getenv('DB_USER', 'svcdb'),
        'password': os.getenv('DB_PASSWORD', 'svcadmin'),
        'host': os.getenv('DB_HOST', 'AWSXE'),
    })
    # TRACK_MODIFICATIONという機能を無効化します
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Trueにしておくと 発行される SQLがログで吐かれる
    SQLALCHEMY_ECHO = True

    # JAVA_LIBパス
    JAVA_LIB = os.environ.get(
        'JAVA_LIB',
        '/home04/svcdb/java_lib')
    # ファイルアップロードパス（一時）
    UPLOAD_TMP_DIR_PATH = os.environ.get(
        'UPLOAD_TMP_DIR_PATH',
        '/home04/svcdb/tmp/file')
    # ファイルアップロードパス
    UPLOAD_DIR_PATH = os.environ.get(
        'UPLOAD_DIR_PATH',
        '/home04/svcdb/svcdb_file_dir')
    # ファイルダウンロードパス
    DOWNLOAD_DIR_PATH = os.environ.get(
        'DOWNLOAD_DIR_PATH',
        '/home04/svcdb/file_dl_dir')
    # 1度の実行で処理するObject数（全文検索用）
    CTX_MAX_OBJECT_CNT = 20
    # ファイル解凍パス（全文検索用：一時）
    UNZIP_DIR_PATH_CTX = os.environ.get(
        'UNZIP_DIR_PATH_CTX',
        '/home04/svcdb/tmp/ctx')
