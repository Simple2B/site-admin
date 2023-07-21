from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

from app.common.models import SuperUser as User
from app import db


class LoginForm(FlaskForm):
    user_id = StringField("Username", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    submit = SubmitField("Login")


class ForgotForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])

    def validate_email(self, email):
        query = User.select().where(User.email == email.data)
        user = db.session.scalar(query)
        if not user:
            raise ValidationError("Email not found")


class ChangePasswordForm(FlaskForm):
    password = PasswordField(
        "Password",
        [
            DataRequired(),
            EqualTo("password_confirmation", message="Passwords must match"),
        ],
        render_kw={"placeholder": "Password"},
    )
    password_confirmation = PasswordField(
        "Repeat Password", render_kw={"placeholder": "Repeat Password"}
    )
    submit = SubmitField("Change password")
