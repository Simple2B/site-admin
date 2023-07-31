from flask_wtf import FlaskForm
from wtforms import (
    StringField,
)
from wtforms.validators import DataRequired, Length


class NewStackForm(FlaskForm):
    stacks = StringField("stacks", [DataRequired(), Length(2, 32)])
