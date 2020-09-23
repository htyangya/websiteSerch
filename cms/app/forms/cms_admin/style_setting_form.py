from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField


class StyleSettingForm(FlaskForm):
    dbId = StringField("db_id", [])
    dbName = StringField("db_name", [])
    styleName = StringField("style_name", validators=[])
    styleType = StringField("style_type", validators=[])
    value = StringField("value", validators=[])
    defaultValue = StringField("default_value", validators=[])
    remarks = TextAreaField("remarks", [])
    submit = SubmitField('Save')
