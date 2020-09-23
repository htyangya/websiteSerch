from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField


class ListFormatForm(FlaskForm):
    formatId = StringField("format_id", [])
    objectTypeId = StringField("object_type_id", [])
    formatType = StringField("format_type", [])
    displayOrder = StringField("display_order", [])
    remarks = TextAreaField("remarks", [])
    submit = SubmitField('Save')
