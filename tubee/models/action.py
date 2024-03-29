"""Action Model"""
from dataclasses import dataclass
from enum import Enum
from typing import Union

from loguru import logger

from .. import db


class ActionType(str, Enum):
    Notification = "Notification"
    Playlist = "Playlist"
    Download = "Download"


@dataclass
class Action(db.Model):  # type: ignore
    """Action to Perform when new video uploaded"""

    id: str
    name: str
    type: ActionType
    details: dict
    username: str
    automate: bool
    channel_id: str
    tag_id: int

    __tablename__ = "action"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    type = db.Column(db.Enum(ActionType), nullable=False)
    details = db.Column(db.JSON, nullable=False, default={})
    username = db.Column(db.String(32), db.ForeignKey("user.username"), nullable=False)
    automate = db.Column(db.Boolean, nullable=False, default=True)
    channel_id = db.Column(db.String(32), db.ForeignKey("channel.id"))
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"))
    __table_args__ = (
        db.ForeignKeyConstraint(
            [username, channel_id], ["subscription.username", "subscription.channel_id"]
        ),
        {},
    )
    channel = db.relationship(
        "Channel", back_populates="actions", overlaps="subscription"
    )
    subscription = db.relationship(
        "Subscription", back_populates="_actions", overlaps="channel"
    )
    tag = db.relationship("Tag", back_populates="actions")
    user = db.relationship("User", back_populates="actions", overlaps="subscription")

    def __init__(self, username: str, params: Union[dict[str, str], None] = None):
        from .subscription import Subscription
        from .tag import Tag

        params = params or {}
        if channel_id := params.get("channel_id"):
            self.channel_id = (
                Subscription.query.filter_by(channel_id=channel_id, username=username)
                .first_or_404()
                .channel_id
            )
        elif tag_id := params.get("tag_id"):
            self.tag_id = (
                Tag.query.filter_by(id=tag_id, username=username).first_or_404().id
            )
        self.username = username
        self.edit(params)
        db.session.add(self)
        db.session.commit()
        logger.info(f"Action <{self.id}>: Create")

    def __repr__(self):
        return f"<Action <{self.id}>: {self.type} by {self.username}>"

    @property
    def action_mixin(self):
        if self.channel_id:
            return self.subscription
        return self.tag

    @action_mixin.setter
    def action_mixin(self, object):
        raise AttributeError("Action Mixin can't be modified")

    def edit(self, new_data):
        modified = {}

        if not self.name or new_data["action_name"] != self.name:
            modified["name"] = new_data["action_name"]
            self.name = new_data["action_name"]

        if not self.type or new_data["action_type"] != self.type.value:
            modified["type"] = new_data["action_type"]
            self.type = new_data["action_type"]

        if self.automate != "automate" in new_data:
            modified["automate"] = bool(new_data["automate"])
            self.automate = bool(new_data["automate"])

        new_details = new_data[new_data["action_type"].lower()]
        if not self.details or new_details != self.details:
            modified["details"] = new_details
            self.details = new_details

        if modified:
            db.session.commit()

        logger.info(f"Action <{self.id}>: modified ({modified})")
        return modified

    def delete(self):
        action_id = self.id
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info(f"Action <{action_id}>: Remove")
            return self
        except Exception as error:
            # TODO: not sure if this is the best way to handle this
            logger.exception(f"Action <{action_id}>: Remove failed")
            raise error

    def execute(self, **parameters):
        if self.type is ActionType.Notification:
            results = self.user.send_notification(
                "Action",
                self.details.get("service", None),
                **parameters,
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
                image_url=self.details.get("image_url", "{video_thumbnail}").format(
                    **parameters
                ),
            )
        elif self.type is ActionType.Playlist:
            results = self.user.insert_video_to_playlist(
                parameters["video_id"],
                playlist_id=self.details.get("playlist_id", None),
                position=self.details.get("position", None),
            )
        elif self.type is ActionType.Download:
            results = self.user.dropbox.files_save_url(
                self.details.get("file_path", "/{video_title}.mp4").format(
                    **parameters
                ),
                parameters["video_file_url"],
            )
            results = str(results)
        else:
            logger.info(f"Action <{self.id}>: Execute without valid type")
            raise RuntimeError("Invalid Action")
        logger.info(f"Action <{self.id}>: Executed ({results})")
        return results
