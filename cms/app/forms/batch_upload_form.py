import os
import uuid

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, BooleanField

from app.lib.cms_lib.str_util import StrUtil
from app.lib.conf.const import Const


class BatchUploadForm(FlaskForm):
    db_id = StringField("db_id")
    object_type_id = StringField("object_type_id")
    upload_file_by_select = FileField("upload_file_by_select")
    upload_file = FileField("upload_file")
    template_id = FileField("template_id")
    skip_null_check = BooleanField("skip_null_check", default=False)

    def get_template_filename(self):
        upload_temp_dir = StrUtil.get_safe_config(current_app, 'UPLOAD_TMP_DIR_PATH')
        return os.path.join(upload_temp_dir, self.template_id.data + Const.FILE_SUFFIX_EXCEL)

    def save_and_get_filename(self):
        upload_temp_dir = StrUtil.get_safe_config(current_app, 'UPLOAD_TMP_DIR_PATH')
        if upload_temp_dir and not os.path.exists(upload_temp_dir):
            os.makedirs(upload_temp_dir, exist_ok=True)
        return self._save_file_temporarily(upload_temp_dir)

    def _save_file_temporarily(self, upload_temp_dir):
        file = self.upload_file.data
        temp_file_info = self.random_temp_filename(file.filename)
        full_file_name = os.path.join(upload_temp_dir, temp_file_info['template_name'])
        file.save(full_file_name)
        return temp_file_info

    @staticmethod
    def random_temp_filename(filename):
        ext = os.path.splitext(filename)[1]
        template_id = uuid.uuid4().hex
        template_name = template_id + ext
        return {'template_id': template_id, 'template_name': template_name}
