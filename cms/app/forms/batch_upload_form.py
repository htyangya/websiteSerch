import os
import uuid

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, BooleanField, IntegerField

from app.lib.cms_lib.str_util import StrUtil


class BatchUploadForm(FlaskForm):
    db_id = StringField("db_id")
    object_type_id = StringField("object_type_id")
    file = FileField("file")
    skip_null_check = BooleanField("skip_null_check", default=False)
    ajax_flag = IntegerField("ajax_flag", default=0)

    def save_and_get_filename(self, is_full_name=True):
        upload_temp_dir = StrUtil.get_safe_config(current_app, 'UPLOAD_TMP_DIR_PATH')
        if upload_temp_dir and not os.path.exists(upload_temp_dir):
            os.makedirs(upload_temp_dir, exist_ok=True)

        if isinstance(self.file.data, str):
            return os.path.join(upload_temp_dir, self.file.data) if is_full_name else self.file.data
        return self._save_file_temporarily(upload_temp_dir, is_full_name)

    def _save_file_temporarily(self, upload_temp_dir, is_full_name=True):
        file = self.file.data
        new_file_name = self.random_filename(file.filename)
        full_file_name = os.path.join(upload_temp_dir, new_file_name)
        file.save(full_file_name)
        return full_file_name if is_full_name else new_file_name

    @staticmethod
    def random_filename(filename):
        ext = os.path.splitext(filename)[1]
        new_filename = uuid.uuid4().hex + ext
        return new_filename
