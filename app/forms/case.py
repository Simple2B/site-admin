from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    BooleanField,
    SelectMultipleField,
    widgets
)
from wtforms.validators import DataRequired, Length


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class NewCaseForm(FlaskForm):
    title = StringField("title", [DataRequired(), Length(2, 32)])
    sub_title = StringField("sub_title", [DataRequired(), Length(2, 64)])
    description = StringField("description", [DataRequired(), Length(1, 512)])
    is_active = BooleanField("is_active")
    project_link = StringField("project_link")
    role = StringField("role", [DataRequired(), Length(6, 32)])
    stacks = MultiCheckboxField('stacks')

    submit = SubmitField("Save")
