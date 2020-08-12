from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField


class ListFormatForm(FlaskForm):
    formatId = StringField("format_id", [])
    objectTypeId = StringField("object_type_id", [])
    formatType = SelectField("format_type", choices=[('LIST', 'LIST'), ('PROPERTY', 'PROPERTY')], validators=[])

    displayOrder = StringField("display_order", [])
    remarks = TextAreaField("remarks", [])
    submit = SubmitField('Save')
