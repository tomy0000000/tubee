"""Forms"""
from flask_wtf import FlaskForm
from wtforms.fields import (
    HiddenField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    EqualTo,
    Length,
)
from .models import ActionType


class LoginForm(FlaskForm):
    """Login form"""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=6, max=30)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=20)]
    )
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    """Register form"""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=6, max=30)]
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6, max=20),
            EqualTo("password_confirm", message="Password Mismatched!"),
        ],
    )
    password_confirm = PasswordField(
        "Password Confirm",
        validators=[
            DataRequired(),
            Length(min=6, max=20),
            EqualTo("password", message="Password Mismatched!"),
        ],
    )
    submit = SubmitField("Register")


class ActionForm(FlaskForm):
    """Action Form"""

    action_name = StringField("Name", validators=[Length(max=32)])
    action_type = SelectField(
        "Type",
        validators=[DataRequired()],
        choices=[(item.name, item.value) for item in ActionType],
    )
    channel_id = HiddenField("Channel ID", validators=[DataRequired()])
