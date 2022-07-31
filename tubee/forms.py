"""Forms"""
from flask_wtf import FlaskForm
from wtforms.fields import (
    FormField,
    HiddenField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, EqualTo, Length

from .models import ActionType, Service


class LoginForm(FlaskForm):
    """Login form"""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
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
            Length(min=6, max=30),
            EqualTo("password_confirm", message="Password Mismatched!"),
        ],
    )
    password_confirm = PasswordField(
        "Password Confirm",
        validators=[
            DataRequired(),
            Length(min=6, max=30),
            EqualTo("password", message="Password Mismatched!"),
        ],
    )
    submit = SubmitField("Register")


class NotificationActionForm(FlaskForm):
    """Keyword Arguments for Notification"""

    class Meta:
        csrf = False

    service = SelectField(
        "Notification Service",
        validators=[DataRequired()],
        choices=[(item.value, item.value) for item in Service],
    )
    message = StringField(
        "Message Body",
        default="{video_title}",
        validators=[DataRequired()],
    )
    title = StringField(
        "Message Title",
        default="New from {channel_name}",
        validators=[DataRequired()],
    )
    url = StringField(
        "URL",
        default="https://www.youtube.com/watch?v={video_id}",
        validators=[DataRequired()],
    )
    url_title = StringField(
        "URL Title",
        default="{video_title}",
        validators=[DataRequired()],
    )
    image_url = StringField(
        "Image URL",
        default="{video_thumbnails}",
        validators=[DataRequired()],
    )


class PlaylistActionForm(FlaskForm):
    """Keyword Arguments for Playlist"""

    class Meta:
        csrf = False

    playlist_id = StringField(
        "Playlist ID",
        validators=[DataRequired()],
    )


class DownloadActionForm(FlaskForm):
    """Keyword Arguments for Download"""

    class Meta:
        csrf = False

    file_path = StringField(
        "File Path",
        default="/{video_title}.mp4",
        validators=[DataRequired()],
    )


class ActionForm(FlaskForm):
    """Action Form"""

    action_name = StringField(
        "Name",
        validators=[DataRequired(), Length(max=32)],
    )
    action_type = SelectField(
        "Type",
        validators=[DataRequired()],
        choices=[(item.value, item.value) for item in ActionType],
    )
    channel_id = HiddenField("Channel ID")
    tag_id = HiddenField("Tag ID")
    notification = FormField(NotificationActionForm)
    playlist = FormField(PlaylistActionForm)
    download = FormField(DownloadActionForm)

    def validate(self):
        if not self.channel_id.data and not self.tag_id.data:
            return False
        action_type = self.action_type.data.lower()
        sub_form = getattr(self, action_type)
        if not sub_form.validate(sub_form):
            return False
        return True
