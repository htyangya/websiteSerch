import os
import uuid

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, BooleanField

from app.lib.cms_lib.str_util import StrUtil


class BatchUploadForm(FlaskForm):
    db_id = StringField("db_id")
    object_type_id = StringField("object_type_id")
    file = FileField("file")
    skip_null_check = BooleanField("skip_null_check", default=False)

    def save_file_temporarily(self):
        upload_temp_dir = StrUtil.get_safe_config(current_app, 'UPLOAD_TMP_DIR_PATH')
        if upload_temp_dir and not os.path.exists(upload_temp_dir):
            os.makedirs(upload_temp_dir, exist_ok=True)
        file = self.file.data
        full_file_name = os.path.join(upload_temp_dir,  self.random_filename(file.filename))
        file.save(full_file_name)
        return full_file_name

    def get_full_tem_filename(self):
        upload_temp_dir = StrUtil.get_safe_config(current_app, 'UPLOAD_TMP_DIR_PATH')
        if upload_temp_dir and not os.path.exists(upload_temp_dir):
            os.makedirs(upload_temp_dir, exist_ok=True)
        return os.path.join(upload_temp_dir, self.file.data)

    @staticmethod
    def random_filename(filename):
        ext = os.path.splitext(filename)[1]
        new_filename = uuid.uuid4().hex + ext
        return new_filename
