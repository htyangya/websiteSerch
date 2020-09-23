from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField


class DatabaseForm(FlaskForm):
    dbId = StringField("db_id", [])
    dbName = StringField("db_name", [])
    sessionCookieName = StringField("session_cookie_name", [])
    displayOrder = StringField("display_order", [])
    loginMessage = TextAreaField("login_message", [])
    informationMessage = TextAreaField("information_message", [])
    remarks = TextAreaField("remarks", [])
    submit = SubmitField('Save')
