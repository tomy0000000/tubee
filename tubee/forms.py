"""Forms for Tubee"""
import wtforms
import flask_wtf


class LoginForm(flask_wtf.FlaskForm):
    """Login form"""
    username = wtforms.TextField("Username",
                                 validators=[
                                     wtforms.validators.InputRequired(),
                                     wtforms.validators.Length(min=6, max=30)
                                 ])
    password = wtforms.PasswordField("Password",
                                     validators=[
                                         wtforms.validators.InputRequired(),
                                         wtforms.validators.Length(min=6,
                                                                   max=20)
                                     ])
    submit = wtforms.SubmitField("Sign In")


class RegisterForm(flask_wtf.FlaskForm):
    """Register form"""
    username = wtforms.TextField("Username",
                                 validators=[
                                     wtforms.validators.InputRequired(),
                                     wtforms.validators.Length(min=6, max=30)
                                 ])
    password = wtforms.PasswordField("Password",
                                     validators=[
                                         wtforms.validators.InputRequired(),
                                         wtforms.validators.Length(min=6,
                                                                   max=20),
                                         wtforms.validators.EqualTo(
                                             "password_confirm",
                                             message="Password Mismatched!")
                                     ])
    password_confirm = wtforms.PasswordField(
        "Password Confirm",
        validators=[
            wtforms.validators.InputRequired(),
            wtforms.validators.Length(min=6, max=20),
            wtforms.validators.EqualTo("password",
                                       message="Password Mismatched!")
        ])
    submit = wtforms.SubmitField("Register")
