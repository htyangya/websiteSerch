from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class PrivsDeptForm(FlaskForm):
    class Meta:
        csrf = False

    corp_cd = StringField("corp_cd")
    div_cd = StringField("div_cd")
    dept_cd = StringField("dept_cd")
    emp_type_cd = StringField("emp_type_cd")
    working_type_cd = StringField("working_type_cd")
    privs_type = StringField("privs_type")

    search = SubmitField("Search")
