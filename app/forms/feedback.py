from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, URL, Optional
from app.common.models import Languages


class NewFeedBackForm(FlaskForm):
    client_name = StringField(
        "client_name",
        [DataRequired(), Length(min=1, max=128)],
        render_kw={"placeholder": "Client Name"},
    )
    project_name = StringField(
        "project_name",
        [Optional(), Length(min=1, max=128)],
        render_kw={"placeholder": "Project Name"},
    )
    link = StringField(
        "link", [Optional(), URL()], render_kw={"placeholder": "https://example.com"}
    )
    comment = TextAreaField(
        "comment",
        [DataRequired(), Length(min=1, max=512)],
        render_kw={"placeholder": "Comment"},
    )
    language = SelectField(
        "language",
        choices=[(lan.value, lan.name) for lan in Languages],
        validators=[DataRequired()],
        default=Languages.ENGLISH.value,
    )


class EditFeedBackForm(NewFeedBackForm):
    uuid = HiddenField("uuid", [DataRequired()])
