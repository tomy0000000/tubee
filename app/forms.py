"""Forms for Tubee"""
import wtforms
import flask_wtf

class LoginForm(flask_wtf.FlaskForm):
    """Login form of Tubee main system"""
    username = wtforms.TextField("Username",
                                 validators=[
                                     wtforms.validators.InputRequired(),
                                     wtforms.validators.Length(min=3, max=30)
                                 ])
    password = wtforms.PasswordField("Password",
                                     validators=[
                                         wtforms.validators.InputRequired(),
                                         wtforms.validators.Length(min=3, max=20)
                                     ])
    submit = wtforms.SubmitField("Sign In")
