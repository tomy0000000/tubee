"""Forms"""
from flask_wtf import FlaskForm
from wtforms.fields import (
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


class LoginForm(FlaskForm):
    """Login form"""
    username = StringField("Username",
                           validators=[DataRequired(),
                                       Length(min=6, max=30)])
    password = PasswordField(
        "Password", validators=[DataRequired(),
                                Length(min=6, max=20)])
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    """Register form"""
    username = StringField("Username",
                           validators=[DataRequired(),
                                       Length(min=6, max=30)])
    password = PasswordField("Password",
                             validators=[
                                 DataRequired(),
                                 Length(min=6, max=20),
                                 EqualTo("password_confirm",
                                         message="Password Mismatched!")
                             ])
    password_confirm = PasswordField("Password Confirm",
                                     validators=[
                                         DataRequired(),
                                         Length(min=6, max=20),
                                         EqualTo(
                                             "password",
                                             message="Password Mismatched!")
                                     ])
    submit = SubmitField("Register")


class ActionForm(FlaskForm):
    """Action Form"""
    action_name = StringField("Name",
                              validators=[DataRequired()],
                              render_kw={"class": "form-control"})
    action_type = SelectField("Type",
                              validators=[DataRequired()],
                              render_kw={"class": "form-control"})
    submit = SubmitField("Save",
                         validators=[DataRequired()],
                         render_kw={"class": "btn btn-success"})
