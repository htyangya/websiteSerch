from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField


class KeywordForm(FlaskForm):
    keywordMstId = StringField("keyword_mst_id", validators=[])
    dbId = StringField("db_id", [])
    dbName = StringField("db_name", [])
    keywordName = StringField("keyword_name", validators=[])
    multiSetFlg = SelectField("multi_set_flg", choices=[('0', '1つ設定可能'), ('1', '複数設定可能')], validators=[])
    notNullFlg = SelectField("not_null_flg", choices=[('0', ''), ('1', '必須')], validators=[])
    treeSeparator = StringField("tree_separator", validators=[])
    keywords = TextAreaField("keywords", validators=[])
    submit = SubmitField('Save')
