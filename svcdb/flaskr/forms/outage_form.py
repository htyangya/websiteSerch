from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, ValidationError


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
    date_start = SelectField("Period", choices=[(str(i), str(i)) for i in range(2019, 2041)],
                             default=lambda: str(datetime.now().year))
    date_end = SelectField("", choices=[(str(i), str(i)) for i in range(2019, 2041)],
                           default=lambda: str(datetime.now().year + 5))

    def validate_date_start(self, field):
        if field.data > self.date_end.data:
            raise ValidationError('')
