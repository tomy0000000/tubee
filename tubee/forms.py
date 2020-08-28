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


class ActionKwargsForm(FlaskForm):
    """Keyword Arguments for Actions"""

    keyword = StringField("keyword", validators=[DataRequired()])
    value = StringField("value", validators=[DataRequired()])


class NotificationActionForm(FlaskForm):
    """Keyword Arguments for Notification"""

    class Meta:
        csrf = False

    service = SelectField(
        "Notification Service",
        validators=[DataRequired()],
        default="Pushover",
        choices=[(item.name, item.value) for item in Service],
        render_kw={"class": "form-control"},
    )
    message = StringField(
        "Message Body",
        default="{video_title}",
        validators=[DataRequired()],
        render_kw={"class": "form-control"},
    )
    title = StringField(
        "Message Title",
        default="New from {channel_name}",
        validators=[DataRequired()],
        render_kw={"class": "form-control"},
    )
    url = StringField(
        "URL",
        default="https://www.youtube.com/watch?v={video_id}",
        validators=[DataRequired()],
        render_kw={"class": "form-control"},
    )
    url_title = StringField(
        "URL Title",
        default="{video_title}",
        validators=[DataRequired()],
        render_kw={"class": "form-control"},
    )
    image_url = StringField(
        "Image URL",
        default="{video_thumbnails}",
        validators=[DataRequired()],
        render_kw={"class": "form-control"},
    )


class PlaylistActionForm(FlaskForm):
    """Keyword Arguments for Playlist"""

    class Meta:
        csrf = False

    playlist_id = StringField(
        "Playlist ID",
        default="WL",
        validators=[DataRequired()],
        render_kw={"class": "form-control"},
    )


class DownloadActionForm(FlaskForm):
    """Keyword Arguments for Download"""

    class Meta:
        csrf = False

    file_path = StringField(
        "File Path",
        default="/{video_title}.mp4",
        validators=[DataRequired()],
        render_kw={"class": "form-control"},
    )


class ActionForm(FlaskForm):
    """Action Form"""

    action_name = StringField(
        "Name", validators=[Length(max=32)], render_kw={"class": "form-control"}
    )
    action_type = SelectField(
        "Type",
        validators=[DataRequired()],
        default="Notification",
        choices=[(item.name, item.value) for item in ActionType],
        render_kw={"class": "form-control"},
    )
    channel_id = HiddenField("Channel ID", validators=[DataRequired()])
    notification = FormField(NotificationActionForm)
    playlist = FormField(PlaylistActionForm)
    download = FormField(DownloadActionForm)

    def validate(self):
        results = True
        if self.action_type.data == "Notification" and not self.notification.validate(
            self
        ):
            results = False
        if self.action_type.data == "Playlist" and not self.playlist.validate(self):
            results = False
        if self.action_type.data == "Download" and not self.download.validate(self):
            results = False
        return results
