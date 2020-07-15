import gzip
import os

from flask import current_app

from app.lib.cms_lib.str_util import StrUtil


class FileUtil:
    def unzip_file(uf, unzipDirPath, file_name):
        df = os.path.join(unzipDirPath, str(file_name))
        try:
            decompressedFile = gzip.open(uf, 'rb')
            if not os.path.isdir(unzipDirPath):
                os.makedirs(unzipDirPath)

            openDf = open(df, 'wb')
            openDf.write(decompressedFile.read())
            decompressedFile.close()
            openDf.close()
            return df
        except Exception as e:
            StrUtil.print_error('unzip_file file_path:{}'.format(str(df)))
            return None

    @staticmethod
    def get_max_upload_file_size():
        max_upload_file_size = StrUtil.get_safe_config(current_app, 'MAX_UPLOAD_FILE_SIZE_MB')
        if not max_upload_file_size or max_upload_file_size <= 0:
            max_upload_file_size = 40
        return max_upload_file_size
