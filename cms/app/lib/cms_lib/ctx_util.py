import os
import re
import shutil
import subprocess
import sys

from sqlalchemy import text

from app import db
from app.lib.cms_lib.file_util import FileUtil
from app.lib.cms_lib.str_util import StrUtil
from app.lib.conf.const import Const
from app.models.cms_admin.cms_ctx_data import CmsCtxData
from app.models.cms_db_admin.cms_db import CmsDb
from app.models.cms.cms_file import CmsFile
from app.models.cms.cms_file_type import CmsFileType
from app.models.cms.cms_object import CmsObject
from app.services.cms_admin.file_service import ctx_allowed_file


class CtxUtil:
    def optimize_ctx(self, app):
        try:
            # データベースオブジェクトを取得する
            db_list = CmsDb.getCmsDbList()
            if db_list is None:
                return False

            row_num = str(StrUtil.get_safe_config(app, 'CTX_MAX_OBJECT_CNT'))

            for db_info in db_list:
                StrUtil.print_debug("optimize_ctx db_id=[{}] begin.".format(str(db_info.db_id)))
                cms_object = CmsObject()
                for object_info in cms_object.getCtxObjectList(db_info.db_id, row_num):
                    cmsCtxData = CmsCtxData()
                    # cms_ctx_dataからレコード削除 (updateされた場合の対応)
                    cmsCtxData.delCmsCtxData(object_info.object_id, db_info.db_id)

                    # タイトルテキスト 例：<#IDX_TEXT_001#> : <#IDX_TEXT_002#>
                    ctx_title_rst = {'CTX_TITLE': '', 'CTX_TEXT': '', 'CTX_ERROR_FLG': 0, 'CTX_ERROR_LOG': ''}
                    cms_object.getCtxTitle(
                        object_info.object_type_id,
                        object_info.object_id,
                        None,
                        object_info.ctx_title_format,
                        ctx_title_rst)

                    # cms_ctx_dataに登録する情報を設定する
                    cmsCtxData.db_id = db_info.db_id
                    cmsCtxData.object_id = object_info.object_id
                    cmsCtxData.object_updated_at = object_info.updated_at
                    cmsCtxData.ctx_title = ctx_title_rst['CTX_TITLE']
                    cmsCtxData.ctx_text = ctx_title_rst['CTX_TEXT']
                    cmsCtxData.ctx_error_log = ctx_title_rst['CTX_ERROR_LOG']
                    cmsCtxData.data_type = Const.DATA_TYPE_OBJECT
                    url = Const.URL_FORMAT.format(
                        str(StrUtil.get_safe_config(app, 'CMS_SYS_URL')).strip('/') + '/property',
                        'func={}&db_id={}&id={}&object_id={}'.format(
                            'show_property',
                            db_info.db_id,
                            object_info.parent_folder_id,
                            object_info.object_id)
                    )
                    cmsCtxData.ctx_url = url
                    cmsCtxData.ctx_error_flg = ctx_title_rst['CTX_ERROR_FLG']

                    # cms_ctx_dataに登録する
                    cmsCtxData.addCmsCtxData(cmsCtxData)

                    # INDEXに登録したら、 cms_object.ctx_indexed_flg=1にする
                    cms_object.ctxUpdObject(object_info.object_id, 1)

                    # cms_object_property, cms_file_typeからINDEX対象の属性やファイルを特定
                    cms_file = CmsFile()
                    for file_info in cms_file.get_ctx_file_list(object_info.object_id):
                        if not ctx_allowed_file(file_info.file_name):
                            continue
                        cmsCtxData = CmsCtxData()

                        # ctx_text = ctx_text_format.format(ctx_text,
                        #                                   file_info.file_name + ":"
                        #                                   + os.path.join(file_info.dir_name,
                        #                                                  file_info.c_file_name))
                        StrUtil.print_debug('ctx_file file_info=[file_name={}; file_path={}]'.format(
                            file_info.file_name,
                            os.path.join(file_info.dir_name,
                                         file_info.c_file_name)))

                        # CTX_TITLE_FOTMATの取得
                        cmsFileType = CmsFileType()
                        fileTypeInfo = cmsFileType.getFileTypeInfo(file_info.file_type_id)

                        # タイトルテキスト 例：<#IDX_TEXT_001#> : <#IDX_TEXT_002#> (<#FILE_NAME#>)
                        ctx_title_rst = {'CTX_TITLE': '', 'CTX_TEXT': '', 'CTX_ERROR_FLG': 0, 'CTX_ERROR_LOG': ''}
                        cms_object.getCtxTitle(
                            object_info.object_type_id,
                            object_info.object_id,
                            file_info.file_id,
                            fileTypeInfo.ctx_title_format,
                            ctx_title_rst)

                        ctx_text_rst = {'CTX_TEXT': '', 'CTX_ERROR_FLG·': 0, 'CTX_ERROR_LOG': ''}
                        CtxUtil._get_ctx_text(app, file_info, ctx_text_rst)

                        # URL
                        url = ''
                        # テキスト
                        ctx_text = Const.CONTACT_FORMAT.format(ctx_title_rst['CTX_TEXT'], ctx_text_rst['CTX_TEXT'])
                        # エラーメッセージ
                        ctx_error_log = ctx_title_rst['CTX_ERROR_LOG']
                        if len(ctx_error_log) != 0:
                            ctx_error_log += '\n'
                        ctx_error_log += ctx_text_rst['CTX_ERROR_LOG']

                        # cms_ctx_dataに登録する情報を設定する
                        cmsCtxData.db_id = db_info.db_id
                        cmsCtxData.object_id = object_info.object_id
                        cmsCtxData.object_updated_at = object_info.updated_at
                        cmsCtxData.ctx_title = ctx_title_rst['CTX_TITLE']
                        cmsCtxData.ctx_text = ctx_text
                        cmsCtxData.ctx_error_log = StrUtil.truncate(ctx_error_log, 4000)
                        cmsCtxData.data_type = Const.DATA_TYPE_FILE
                        if ctx_text_rst['CTX_ERROR_FLG'] == 0:
                            url = Const.URL_FORMAT.format(
                                str(StrUtil.get_safe_config(app, 'CMS_SYS_URL')).strip('/') + '/download_file',
                                'db_id={}&file_id={}'.format(db_info.db_id, file_info.file_id)
                            )
                        cmsCtxData.ctx_url = url
                        cmsCtxData.ctx_error_flg = ctx_text_rst['CTX_ERROR_FLG']

                        # cms_ctx_dataに登録する
                        cmsCtxData.addCmsCtxData(cmsCtxData)

                        cms_file = CmsFile(object_info.object_id)
                        # INDEXに登録したら、 cms_file.ctx_indexed_flg=1にする
                        cms_file.setCtxIndexedFlg(file_info.file_id, 1)

                    # DBごと処理後にtmpフォルダを空にする
                    CtxUtil._tmp_file_remove(app)
                StrUtil.print_debug('optimize_ctx db_id=[{}] end.'.format(str(db_info.db_id)))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            tb = sys.exc_info()[2]
            StrUtil.print_error('optimize_ctx error_msg:{}'.format(str(e.with_traceback(tb))))
            CtxUtil._tmp_file_remove(app)

    def _get_ctx_text(app, file_info, ctx_text_rst):

        file_path = os.path.join(file_info.dir_name, file_info.c_file_name)
        if not os.path.isfile(file_path):
            ctx_text_rst['CTX_TEXT'] = ''
            ctx_text_rst['CTX_ERROR_FLG'] = 1
            ctx_text_rst['CTX_ERROR_LOG'] = Const.NO_FILE_FOUND_MSG.format(file_path)
            return

        # 解凍パスを取得する
        unzip_dir_path = str(StrUtil.get_safe_config(app, 'UNZIP_DIR_PATH_CTX'))

        # ファイルを解凍する
        tmp_file_name = Const.FILE_EXTENSION_FORMAT.format(file_info.file_id,
                                                           file_info.file_name.rsplit('.', 1)[1].lower())
        unzip_file_path = FileUtil.unzip_file(file_path, unzip_dir_path, tmp_file_name)

        # ファイル存在しないか解凍失敗の場合
        if unzip_file_path is None:
            ctx_text_rst['CTX_TEXT'] = ''
            ctx_text_rst['CTX_ERROR_FLG'] = 1
            ctx_text_rst['CTX_ERROR_LOG'] = Const.UNZIP_ERROR_MSG.format(unzip_file_path)
            return

        try:
            # 設定ファイルからJAVA_LIBを取得
            java_lib = str(StrUtil.get_safe_config(app, 'JAVA_LIB'))

            # PDFファイルのテキスト抽出
            cmd = '{java_bin} -jar {java_lib} -t {file_path}'.format(**{
                'java_bin': '/usr/java/jdk1.8.0_40/bin/java',
                'java_lib': os.path.join(java_lib, 'tika-app-1.23.jar'),
                'file_path': unzip_file_path,
            })

            completed_process = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # 子プロセスが異常終了の場合
            if completed_process.returncode != 0:
                ctx_text_rst['CTX_TEXT'] = ''
                ctx_text_rst['CTX_ERROR_FLG'] = 1
                ctx_text_rst['CTX_ERROR_LOG'] = completed_process.stderr.decode('utf-8')
                return

            ctx_text_rst['CTX_TEXT'] = completed_process.stdout.decode('utf-8')
            ctx_text_rst['CTX_ERROR_FLG'] = 0
            ctx_text_rst['CTX_ERROR_LOG'] = ''
        except Exception as e:
            tb = sys.exc_info()[2]
            StrUtil.print_error("subprocess.run info:{} error_msg:{}".format(
                'file_name:{} file_path:{}/{}'.format(
                    file_info.file_name, file_info.dir_name, file_info.c_file_name
                ),
                str(e.with_traceback(tb)))
            )
            ctx_text_rst['CTX_TEXT'] = ''
            ctx_text_rst['CTX_ERROR_FLG'] = 1
            ctx_text_rst['CTX_ERROR_LOG'] = Const.CONTACT_FORMAT.format(
                cmd,
                Const.CMD_ERROR_MSG.format(str(e.with_traceback(tb))))

    def _tmp_file_remove(app):
        # 解凍パスを取得する
        unzip_dir_path = str(StrUtil.get_safe_config(app, 'UNZIP_DIR_PATH_CTX'))
        if os.path.exists(unzip_dir_path):
            shutil.rmtree(unzip_dir_path)

    def process_ctx_search_text(search_text, search_opt='and_search'):
        join_str = ' | '
        if search_opt == 'and_search':
            join_str = ' & '

        ctx_cond = ''
        search_text_arr = search_text.split()

        for t in search_text_arr:
            #
            # 全文検索の条件
            #  英字(a-zA-Z)の前後に'%'を付ける
            #  その他は'%'をつけない
            #  '%火EIS%'などとするとエラーになる
            #
            if ctx_cond != '':
                ctx_cond += join_str

            t = CtxUtil._escape_contains_special_char(t)
            first_ch = t[0]
            last_ch = t[-1]

            if re.search('^[a-zA-Z0-9]', first_ch) and re.search('^[a-zA-Z0-9]', last_ch):
                ctx_cond = '%' + t + '%'
            else:
                # Note: "様式1" -> "様式1%"のようにすると検索できないことがある
                # ので、以下のようにする
                #   "様式1" -> "( 様式1 | 様式1%" )にする
                #   "A様式" -> "( A様式 | %A様式" )にする
                if re.search('^[a-zA-Z0-9]', first_ch):
                    ctx_cond += '( {} | %{} )'.format(t, t)
                elif re.search('^[a-zA-Z0-9]', last_ch):
                    ctx_cond += '( {} | {}% )'.format(t, t)
                else:
                    ctx_cond += t

        return ctx_cond

    def _escape_contains_special_char(str):
        special_chars = ',&=?{}\\()[]-;~|$!>*%_'
        special_chars = re.sub(r'(.)', r'\\\1', special_chars)

        str = re.sub(r'([' + special_chars + '])', r'\\\1', str)

        return str

    def reset_ctx_index(self):
        # CMS_CTX_DATA削除
        deleteSql = '''
            DELETE FROM CMS_CTX_DATA
        '''
        db.session.execute(text(deleteSql), {})

        # CMS_OBJECTのCTX_INDEXED_FLGを「0」にする
        updateSql = '''
            UPDATE CMS_OBJECT O
            SET O.CTX_INDEXED_FLG = 0
            WHERE O.IS_DELETED = 0
            AND O.CTX_INDEXED_FLG = 1
        '''
        db.session.execute(text(updateSql), {})

        # CMS_FILEのCTX_INDEXED_FLGを「0」にする
        updateSql = '''
            UPDATE CMS_FILE F
            SET F.CTX_INDEXED_FLG = 0
            WHERE F.IS_DELETED = 0
            AND F.CTX_INDEXED_FLG = 1
        '''
        db.session.execute(text(updateSql), {})
        db.session.commit()
