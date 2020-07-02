from datetime import datetime

from flask import Markup
from flask_login import current_user
from sqlalchemy import Sequence

from flaskr import db


class OutageSchedule(db.Model):
    __tablename__ = 'OUTAGE_SCHEDULE'

    turbine_id = db.Column(db.String())
    id_seq = Sequence('OBJECT_ID_SEQUENCE')
    teiken_id = db.Column(db.Integer, id_seq,
                          server_default=id_seq.next_value(), primary_key=True)
    description = db.Column(db.String())
    outage_start = db.Column(db.Date)
    outage_end = db.Column(db.Date)
    outage_duration = db.Column(db.Integer)
    outage_type_t = db.Column(db.String())
    outage_type_g = db.Column(db.String())
    execution = db.Column(db.Integer)
    pr_date_m = db.Column(db.DateTime)
    pr_date_e = db.Column(db.DateTime)
    representive_id = db.Column(db.String())
    representive_name = db.Column(db.String())
    created_at = db.Column(db.DateTime, default=datetime.now)
    created_by = db.Column(db.String(), default=lambda: current_user.get_id())
    created_by_name = db.Column(db.String(), default=lambda: current_user.get_user_person_name())
    updated_at = db.Column(db.DateTime, default=datetime.now)
    updated_by = db.Column(db.String(), default=lambda: current_user.get_id())
    updated_by_name = db.Column(db.String(), default=lambda: current_user.get_user_person_name())
    delete_flg = db.Column(db.Integer(), default=0)
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.String)
    deleted_by_name = db.Column(db.String())
    _outage_type_mapping = {
        '1': "Major",
        '2': "Minor",
        '3': "Other",
        '4': "N/A",
    }

    @property
    def description_html(self):
        if self.description is None:
            return Markup("")
        return Markup(str(Markup.escape(self.description)).replace("\r\n", "</br>").replace(" ", "&nbsp;"))

    @property
    def outage_type_t_nm(self):
        return 'Turbine: ' + self._outage_type_mapping.get(self.outage_type_t, "")

    @property
    def outage_type_g_nm(self):
        return 'Turbine: ' + self._outage_type_mapping.get(self.outage_type_g, "")

    @property
    def outage_type_nm(self):
        return self.outage_type_t_nm + ', ' + self.outage_type_g_nm
