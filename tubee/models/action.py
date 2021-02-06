"""Action Model"""
from enum import Enum

from .. import db


class ActionType(Enum):
    Notification = "Notification"
    Playlist = "Playlist"
    Download = "Download"


class Action(db.Model):
    """Action to Perform when new video uploaded"""

    __tablename__ = "action"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    type = db.Column(db.Enum(ActionType), nullable=False)
    details = db.Column(db.JSON)
    username = db.Column(db.String(32), db.ForeignKey("user.username"), nullable=False)
    channel_id = db.Column(db.String(32), db.ForeignKey("channel.id"))
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"))
    __table_args__ = (
        db.ForeignKeyConstraint(
            [username, channel_id], ["subscription.username", "subscription.channel_id"]
        ),
        {},
    )
    channel = db.relationship("Channel", back_populates="actions")
    subscription = db.relationship("Subscription", back_populates="_actions")
    tag = db.relationship("Tag", back_populates="actions")
    user = db.relationship("User", back_populates="actions")

    def __init__(self, action_name, action_type, user, action_mixin, details=None):
        from .tag import Tag
        from .subscription import Subscription

        self.name = action_name
        self.type = (
            action_type if action_type is ActionType else ActionType(action_type)
        )
        self.username = user.username
        if isinstance(action_mixin, Subscription):
            self.channel_id = action_mixin.channel_id
        elif isinstance(action_mixin, Tag):
            self.tag_id = action_mixin.id
        else:
            raise ValueError("At least one of <Channel, Tag> must be given")
        self.details = details
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<Action: {self.type} associate with user {self.username}>"

    @property
    def action_mixin(self):
        if self.channel_id:
            return self.subscription
        return self.tag

    @action_mixin.setter
    def action_mixin(self, object):
        raise AttributeError("Action Mixin can't be modified")

    def edit(self, new_data):
        if new_data["action_type"] == "Notification":
            details = new_data["notification"]
        elif new_data["action_type"] == "Playlist":
            details = new_data["playlist"]
        elif new_data["action_type"] == "Download":
            details = new_data["download"]

        modified = {}
        if new_data["action_name"] != self.name:
            modified["name"] = {"old": self.name, "new": new_data["action_name"]}
            self.name = new_data["action_name"]
        if new_data["action_type"] != self.type.value:
            modified["type"] = {"old": self.type.value, "new": new_data["action_type"]}
            self.type = new_data["action_type"]
        if details != self.details:
            modified["details"] = {"old": self.details, "new": details}
            self.details = details

        if modified:
            db.session.commit()

        return modified

    def execute(self, **parameters):
        if self.type is ActionType.Notification:
            return self.user.send_notification(
                "Action",
                self.details.get("service", None),
                message=self.details.get("message", "{video_title}").format(
                    **parameters
                ),
                title=self.details.get("title", "New from {channel_name}").format(
                    **parameters
                ),
                url=self.details.get(
                    "url", "https://www.youtube.com/watch?v={video_id}"
                ).format(**parameters),
                url_title=self.details.get("url_title", "{video_title}").format(
                    **parameters
                ),
                image_url=self.details.get("image_url", "{video_thumbnails}").format(
                    **parameters
                ),
            )
        if self.type is ActionType.Playlist:
            return self.user.insert_video_to_playlist(
                parameters["video_id"],
                playlist_id=self.details.get("playlist_id", None),
                position=self.details.get("position", None),
            )
        if self.type is ActionType.Download:
            return self.user.dropbox.files_save_url(
                self.details.get("file_path", "/{video_title}.mp4").format(
                    **parameters
                ),
                parameters["video_file_url"],
            )
