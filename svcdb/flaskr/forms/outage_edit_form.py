from datetime import datetime
from flaskr.lib.svcdb_lib.db_util import DbUtil
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField
from flaskr.sql import scheduleSql
from flask_login import current_user


class OutageEditForm(FlaskForm):
    class Meta:
        csrf = False

    turbine_id = StringField("turbine_id")
    teiken_id = StringField("teiken_id")
    outage_start = DateField("outage_start", format='%Y/%m/%d')
    outage_end = DateField("outage_end", format='%Y/%m/%d')
    pr_date_m = DateField("1st PR Date(Mechanical)", format='%Y/%m/%d')
    pr_date_e = DateField("1st PR Date(Electric)", format='%Y/%m/%d')
    created_at = DateField("created_at", format='%Y/%m/%d')
    updated_at = DateField("updated_at", format='%Y/%m/%d')
    representive_id = SelectField("representive_id")
    description = TextAreaField("description")
    outage_type_t = StringField("outage_type_t")
    outage_type_g = StringField("outage_type_g")
    outage_duration = StringField("outage_duration")
    execution = StringField("execution")
    country = StringField("Country ")
    plant = StringField("Plant")
    is_close = StringField("is_close")
    is_success = StringField("is_success")
    date_start = SelectField("Period", default=lambda: str(datetime.now().year))
    date_end = SelectField("", default=lambda: str(datetime.now().year + 5))

    def __init__(self, *args, **kwargs):
        super(OutageEditForm, self).__init__(*args, **kwargs)
        rst = DbUtil.sqlExcuter(scheduleSql.fetchRepresentiveSql, tuid=current_user.get_id(),
                                teiken_id=self.teiken_id.data)
        self.representive_id.choices = [("", "")] + [(str(item.representive_id), item.representive_name)
                                                      for item in rst if item.representive_id is not None]
        self.do_init()

    @property
    def representive_name(self):
        return dict(self.representive_id.choices).get(self.representive_id.data)

    def do_init(self):
        if self.outage_end.data and self.outage_start.data:
            self.outage_duration.data = (self.outage_end.data - self.outage_start.data).days
            self.date_start.data = min(self.date_start.data, str(self.outage_start.data.year))
            self.date_end.data = max(self.date_end.data, str(self.outage_end.data.year))
