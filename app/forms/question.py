from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class NewQuestionForm(FlaskForm):
    text = StringField("text", [DataRequired()])
    correct_answer_mark = SelectField(
        "correct_answer_mark",
        choices=[("1", 1), ("2", 2), ("3", 3), ("4", 4)],
        validators=[DataRequired()],
        default=1,
    )
    variant_1 = StringField("variant_1", [DataRequired()])
    variant_2 = StringField("variant_2", [DataRequired()])
    variant_3 = StringField("variant_3", [DataRequired()])
    variant_4 = StringField("variant_4", [DataRequired()])

    submit = SubmitField("Save")


class EditQuestionForm(FlaskForm):
    id = StringField("id", [DataRequired()])
    uuid = StringField("uuid", [DataRequired()])
    text = StringField("text", [DataRequired()])
    correct_answer_mark = SelectField(
        "correct_answer_mark",
        choices=[("1", 1), ("2", 2), ("3", 3), ("4", 4)],
        validators=[DataRequired()],
        default=1,
    )
    variant_1 = StringField("variant_1", [DataRequired()])
    variant_2 = StringField("variant_2", [DataRequired()])
    variant_3 = StringField("variant_3", [DataRequired()])
    variant_4 = StringField("variant_4", [DataRequired()])

    submit = SubmitField("Save")
