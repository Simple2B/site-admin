import filetype

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    BooleanField,
    SelectMultipleField,
    widgets,
    MultipleFileField,
    ValidationError,
)
from wtforms.validators import DataRequired, Length


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class NewCaseForm(FlaskForm):
    id = StringField("id", [DataRequired()])
    title = StringField("title", [DataRequired(), Length(2, 32)])
    sub_title = StringField("sub_title", [DataRequired(), Length(2, 64)])
    case_images = MultipleFileField("case_images", [DataRequired()])
    description = StringField("description", [DataRequired(), Length(1, 512)])
    is_active = BooleanField("is_active")
    is_main = BooleanField("is_main")
    project_link = StringField("project_link")
    role = StringField("role", [DataRequired(), Length(2, 32)])
    stacks = MultiCheckboxField("stacks")
    _screenshots = MultipleFileField("screenshots", [DataRequired()])

    submit = SubmitField("Save")

    def validate_title_image(self, field):
        is_file = filetype.guess(field.data)
        if not is_file or not filetype.is_image(field.data):
            raise ValidationError("File must be an image")

    def validate_sub_title_image(self, field):
        is_file = filetype.guess(field.data)
        if not is_file or not filetype.is_image(field.data):
            raise ValidationError("File must be an image")

    def validate_sub_images(self, field):
        for file in field.data:
            is_file = filetype.guess(file)
            if not is_file or not filetype.is_image(file):
                raise ValidationError("File must be an image")


class UpdateCase(NewCaseForm):
    field = StringField("filed")
