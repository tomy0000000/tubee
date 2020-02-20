"""Action Model"""
from enum import Enum
from uuid import uuid4
from .. import db


class ActionEnum(Enum):
    Notification = "Notification"
    Playlist = "Playlist"
    Download = "Download"


class Action(db.Model):
    """Action to Perform when new video uploaded"""
    __tablename__ = "action"
    action_id = db.Column(db.String(36), primary_key=True)
    action_name = db.Column(db.String(32))
    action_type = db.Column(db.Enum(ActionEnum), nullable=False)
    details = db.Column(db.JSON)
    subscription = db.relationship("Subscription", back_populates="actions")
    subscription_username = db.Column(db.String(32))
    subscription_channel_id = db.Column(db.String(30))
    __table_args__ = (db.ForeignKeyConstraint(
        [subscription_username, subscription_channel_id], [
            "subscription.subscriber_username",
            "subscription.subscribing_channel_id"
        ]), {})

    def __init__(self, action_type, user, channel, details=None):
        self.action_id = str(uuid4())
        self.action_type = action_type if action_type is ActionEnum else ActionEnum(
            action_type)
        self.subscription_username = user.username
        self.subscription_channel_id = channel.channel_id
        self.details = details
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<Action: {} associate with user {} for {}>".format(
            self.action_type, self.user.username, self.channel.channel_id)

    @property
    def user(self):
        from . import User
        return User.query.get(self.subscription_username)

    @user.setter
    def user(self, user_id):
        raise AttributeError("User can't be modified")

    @property
    def channel(self):
        from . import Channel
        return Channel.query.get(self.subscription_channel_id)

    @channel.setter
    def channel(self, channel_id):
        raise AttributeError("Channel can't be modified")

    def execute(self, **parameters):
        if self.action_type is ActionEnum.Notification:
            return self.user.send_notification(
                "Action", self.details.get("service", None), **parameters)
        if self.action_type is ActionEnum.Playlist:
            return self.user.insert_video_to_playlist(
                parameters["video_id"],
                playlist_id=self.details.get("playlist_id", None),
                position=self.details.get("position", None))
