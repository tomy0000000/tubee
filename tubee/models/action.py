"""Action Model"""
from enum import Enum
from uuid import uuid4
from .. import db


class ActionEnum(Enum):
    NOTIFICATION = 1
    PLAYLIST = 2
    DOWNLOAD = 3


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

    def __init__(self, action_type, details=None):
        self.action_id = str(uuid4())
        self.action_type = action_type
        self.details = details
        db.session.add(self)
        db.session.commit()

    # def __repr__(self):
    #     return "<Action: {} associate with user {} for {}>".format(
    #         self.action_type, self.user.username, self.channel.channel_id)
