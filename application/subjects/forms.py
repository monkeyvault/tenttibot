from flask_wtf import FlaskForm
from wtforms import StringField, validators

class SubjectForm(FlaskForm):
    name = StringField("Subject", [validators.Length(min=2)])
 
    class Meta:
        csrf = False