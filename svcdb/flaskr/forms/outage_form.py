from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, ValidationError, IntegerField


class OutageForm(FlaskForm):
    class Meta:
        csrf = False

    turbine_id = StringField("Turbine ID ")
    teiken_id = StringField("Teiken ID ")
    country = SelectField("Country ", choices={})
    plant = StringField("Plant")

    c1 = BooleanField("Registerd")
    c2 = BooleanField('My Project')
    c3 = BooleanField('Mechanical', default=True)
    c4 = BooleanField('Electrical', default=True)
    search = SubmitField("Search")
    date_start = SelectField("Period")
    date_end = SelectField("")
    page = IntegerField(default=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date_start.choices = [(i, i) for i in map(str, range(datetime.now().year - 1, datetime.now().year + 21))]
        self.date_start.default = str(datetime.now().year)
        self.date_end.choices = [(i, i) for i in map(str, range(datetime.now().year + 4, datetime.now().year + 26))]
        self.date_end.default = str(datetime.now().year + 5)

    def validate_date_start(self, field):
        if field.data > self.date_end.data:
            raise ValidationError('')
