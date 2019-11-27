"""Action Model"""
from enum import Enum
from .. import db


class ActionEnum(Enum):
    NOTIFICATION = 1
    PLAYLIST = 2
    DOWNLOAD = 3


class Action(db.Model):
    """Action to Perform when new video uploaded"""
    __tablename__ = "action"
    action_id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.Enum(ActionEnum), nullable=False)
    details = db.Column(db.String(32))
    # subscription_username = db.Column(db.String(30))
    # subscription_channel_id = db.Column(db.String(30))
    # __table_args__ = (db.ForeignKeyConstraint(
    #     [subscription_username, subscription_channel_id], [
    #         "Subscription.subscriber_username",
    #         "Subscription.subscribing_channel_id"
    #     ]), {})

    def __init__(self, action_type, details=None):
        self.action_type = action_type
        self.details = details

    # def __repr__(self):
    #     return "<Action: {} associate with user {} for {}>".format(
    #         self.action_type, self.user.username, self.channel.channel_id)
