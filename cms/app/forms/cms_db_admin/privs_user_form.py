from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class PrivsUserForm(FlaskForm):
    class Meta:
        csrf = False

    user_id = StringField("user_id")
    user_name = StringField("user_name")
    dept_cd = StringField("dept_cd")
    privs_type = StringField("privs_type")

    search = SubmitField("Search")
