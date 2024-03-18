"""Forms"""

from flask_wtf import FlaskForm
from wtforms.fields import (
    BooleanField,
    FormField,
    HiddenField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import AnyOf, DataRequired, EqualTo, Length

from .models import ActionType, Service


class UserForm(FlaskForm):
    """Form for register and password change"""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=6, max=30)]
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6, max=30),
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
    submit = SubmitField()

    def __init__(
        self, submit_label: str, password_confirm: bool = False, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.submit.label.text = submit_label
        if not password_confirm:
            del self.password_confirm


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
        default="{video_thumbnail}",
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
        validators=[DataRequired(), AnyOf([item.value for item in ActionType])],
        choices=[(item.value, item.value) for item in ActionType],
    )
    automate = BooleanField("Automate")
    channel_id = HiddenField("Channel ID")
    tag_id = HiddenField("Tag ID")
    notification = FormField(NotificationActionForm)
    playlist = FormField(PlaylistActionForm)
    download = FormField(DownloadActionForm)

    def validate_automate(self, field):
        if not self.channel_id.data and not self.tag_id.data and field.data:
            field.errors = ["Automate can only be enabled for channels or tags"]

    def validate(self):
        if not self.action_name.validate(self) or not self.action_type.validate(self):
            return False
        if not self.validate_automate(self.automate):
            return False
        if not (action_type := self.action_type.data):
            return False
        sub_form = getattr(self, action_type.lower())
        if not sub_form.validate(sub_form):
            return False
        return True
