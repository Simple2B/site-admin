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
)
from wtforms.validators import DataRequired, Length, URL
from app.database import db
from app.common.models import Case


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class NewCaseForm(FlaskForm):
    title = StringField("title", [DataRequired(), Length(2, 32)])
    sub_title = StringField("sub_title", [DataRequired(), Length(2, 64)])
    title_image = FileField("title_image", [DataRequired()])
    sub_title_image = FileField("sub_title_image", [DataRequired()])
    description = StringField("description", [DataRequired(), Length(1, 512)])
    is_active = BooleanField("is_active")
    is_main = BooleanField("is_main")
    project_link = StringField("project_link", [DataRequired(), URL()])
    role = StringField("role", [DataRequired(), Length(2, 32)])
    stacks = MultiCheckboxField("stacks")
    sub_images = MultipleFileField("sub_images", [DataRequired()])

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


class UpdateCaseState(FlaskForm):
    field = StringField("filed")


class UpdateCase(FlaskForm):
    case_id = IntegerField("case_id", [DataRequired()])
    title = StringField("title", [Length(2, 32)])
    sub_title = StringField("sub_title", [Length(2, 64)])
    main_image = FileField("title_image")
    preview_image = FileField("sub_title_image")
    description = StringField("description", [Length(1, 512)])
    is_active = BooleanField("is_active")
    is_main = BooleanField("is_main")
    project_link = StringField("project_link")
    role = StringField("role", [Length(2, 32)])
    stacks = MultiCheckboxField("stacks")
    screenshots = MultipleFileField(
        "screenshots",
    )

    def validate_title(self, field):
        case_name = db.session.scalars(
            select(Case)
            .where(Case.title == field.data)
            .where(Case.id != int(self.case_id.data))
        ).first()
        if case_name:
            raise ValidationError("This case name is already taken. Must be unique.")

    def validate_stacks(form, field):
        if not field.data:
            raise ValidationError("Select at least one stack.")

    def validate_title_image(self, field):
        if not field.data:
            return
        is_file = filetype.guess(field.data)
        if not is_file or not filetype.is_image(field.data):
            raise ValidationError("File must be an image")

    def validate_sub_title_image(self, field):
        if not field.data:
            return
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
