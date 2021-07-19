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
from wtforms.widgets import HiddenInput

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


class TagForm(FlaskForm):
    """Base Tag Form, also for removing tag"""

    tag_name = StringField(
        "Tag",
        validators=[DataRequired(), Length(max=32)],
    )

    def __init__(self, *args, **kwargs):
        hidden_mode = kwargs.pop("hidden_mode", False)
        super().__init__(*args, **kwargs)
        if hidden_mode:
            self.tag_name.widget = HiddenInput()


class TagSubscriptionForm(TagForm):
    """Tag Form for editing subscription tag"""

    channel_id = HiddenField("Channel ID", validators=[DataRequired()])


class TagRenameForm(FlaskForm):
    """Tag Form for renaming tag"""

    tag_name = HiddenField("Tag", validators=[DataRequired(), Length(max=32)])
    new_tag_name = StringField(
        "New Tag",
        validators=[DataRequired(), Length(max=32)],
    )


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
        choices=[(item.name, item.value) for item in Service],
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
        default="WL",
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
        choices=[(item.name, item.value) for item in ActionType],
    )
    channel_id = HiddenField("Channel ID")
    tag = HiddenField("Tag")
    notification = FormField(NotificationActionForm)
    playlist = FormField(PlaylistActionForm)
    download = FormField(DownloadActionForm)

    def validate(self):
        if not self.channel_id.data and not self.tag.data:
            return False
        if self.action_type.data == "Notification" and not self.notification.validate(
            self
        ):
            return False
        if self.action_type.data == "Playlist" and not self.playlist.validate(self):
            return False
        if self.action_type.data == "Download" and not self.download.validate(self):
            return False
        return True
