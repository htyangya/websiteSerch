from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField


class IpAddrForm(FlaskForm):
    ipAddrListId = StringField("ip_addr_list_id", [])
    ipAddress = StringField("ip_address", [])
    ipAddressOrg = StringField("ip_address_org", [])
    subnetMask = StringField("subnet_mask", [])
    remarks = TextAreaField("remarks", [])
    submit = SubmitField('Save')
