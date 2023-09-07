import filetype

from sqlalchemy import select
from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    StringField,
    SubmitField,
    BooleanField,
    SelectMultipleField,
    widgets,
    FileField,
    MultipleFileField,
    ValidationError,
    SelectField,
)
from wtforms.validators import DataRequired, Length, URL
from app.database import db
from app.common.models import Case, Languages


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class CaseForm(FlaskForm):
    title = StringField("title", [DataRequired(), Length(2, 32)])
    sub_title = StringField("sub_title", [DataRequired(), Length(2, 64)])
    description = StringField("description", [DataRequired(), Length(1, 512)])
    is_active = BooleanField("is_active")
    is_main = BooleanField("is_main")
    project_link = StringField("project_link", [DataRequired(), URL()])
    role = StringField("role", [DataRequired(), Length(2, 32)])
    stacks = MultiCheckboxField("stacks")

    submit = SubmitField("Save")

    def validate_title(self, field):
        case_name = db.session.scalars(
            select(Case).where(Case.title == field.data)
        ).first()
        if case_name:
            raise ValidationError("This case name is already taken. Must be unique.")

    def validate_stacks(form, field):
        if not field.data:
            raise ValidationError("Select at least one stack.")


class NewCaseForm(CaseForm):
    title_image = FileField("title_image", [DataRequired()])
    sub_title_image = FileField("sub_title_image", [DataRequired()])
    sub_images = MultipleFileField("sub_images", [DataRequired()])
    language = SelectField(
        "language",
        choices=[(lan.value, lan.name) for lan in Languages],
        validators=[DataRequired()],
    )


class UpdateCaseState(FlaskForm):
    field = StringField("filed")


class UpdateCase(CaseForm):
    case_id = IntegerField("case_id", [DataRequired()])
    stacks = MultiCheckboxField("stacks")
    title_image = FileField("title_image")
    sub_title_image = FileField("sub_title_image")
    sub_images = MultipleFileField("sub_images")

    def validate_title(self, field):
        case_name = db.session.scalars(
            select(Case)
            .where(Case.title == field.data)
            .where(Case.id != int(self.case_id.data))
        ).first()
        if case_name:
            raise ValidationError("This case name is already taken. Must be unique.")

    def validate_title_image(self, field):
        if field.data:
            is_file = filetype.guess(field.data)
            if not is_file or not filetype.is_image(field.data):
                raise ValidationError("File must be an image")

    def validate_sub_title_image(self, field):
        if field.data:
            is_file = filetype.guess(field.data)
            if not is_file or not filetype.is_image(field.data):
                raise ValidationError("File must be an image")

    def validate_sub_images(self, field):
        for file in field.data:
            # when we not send any file it will come application/octet-stream
            if file.content_type == "application/octet-stream":
                continue
            is_file = filetype.guess(file)
            if not is_file or not filetype.is_image(file):
                raise ValidationError("File must be an image")
