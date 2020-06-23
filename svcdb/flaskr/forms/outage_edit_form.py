from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField


class OutageEditForm(FlaskForm):
    class Meta:
        csrf = False

    turbine_id = StringField("turbine_id")
    teiken_id = StringField("teiken_id")
    # data_type = StringField("data_type")
    outage_start = DateField("outage_start", format='%Y/%m/%d')
    outage_end = DateField("outage_end", format='%Y/%m/%d')
    pr_date_m = DateField("1st PR Date(Mechanical)", format='%Y/%m/%d')
    pr_date_e = DateField("1st PR Date(Electric)", format='%Y/%m/%d')
    description = TextAreaField("description")
    outage_type_t = StringField("outage_type_t")
    outage_type_g = StringField("outage_type_g")
    outage_duration = StringField("outage_duration")
    execution = StringField("execution")
    country = StringField("Country ")
    plant = StringField("Plant")
    is_close = StringField("is_close")
    is_success = StringField("is_success")
    date_start = SelectField("Period", choices=[(str(i), str(i)) for i in range(2019, 2041)],
                             default=lambda: str(datetime.now().year))
    date_end = SelectField("", choices=[(str(i), str(i)) for i in range(2019, 2041)],
                           default=lambda: str(datetime.now().year + 5))

    def __init__(self, *args, **kwargs):
        super(OutageEditForm, self).__init__(*args, **kwargs)
        self.do_init()

    def do_init(self):
        if self.outage_end.data and self.outage_start.data:
            self.outage_duration.data = (self.outage_end.data - self.outage_start.data).days
            self.date_start.data = min(self.date_start.data, str(self.outage_start.data.year))
            self.date_end.data = max(self.date_end.data, str(self.outage_end.data.year))
