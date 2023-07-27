import filetype

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    BooleanField,
    SelectMultipleField,
    widgets,
    FileField,
    MultipleFileField,
    ValidationError
)
from wtforms.validators import DataRequired, Length


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class NewCaseForm(FlaskForm):
    title = StringField("title", [DataRequired(), Length(2, 32)])
    sub_title = StringField("sub_title", [DataRequired(), Length(2, 64)])
    title_image = FileField('title_image', [DataRequired()])
    sub_title_image = FileField('sub_title_image', [DataRequired()])
    description = StringField("description", [DataRequired(), Length(1, 512)])
    is_active = BooleanField("is_active")
    project_link = StringField("project_link")
    role = StringField("role", [DataRequired(), Length(2, 32)])
    stacks = MultiCheckboxField('stacks')
    sub_images = MultipleFileField("sub_images", [DataRequired()])

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


