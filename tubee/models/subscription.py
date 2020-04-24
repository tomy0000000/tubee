"""Subscription Model"""
from datetime import datetime

from .. import db
from .action import Action
from .subscription_tag import SubscriptionTag


class Subscription(db.Model):
    """Relationship between User and Channel"""

    __tablename__ = "subscription"
    username = db.Column(
        db.String(32), db.ForeignKey("user.username"), primary_key=True
    )
    channel_id = db.Column(db.String(32), db.ForeignKey("channel.id"), primary_key=True)
    subscribe_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    unsubscribe_timestamp = db.Column(db.DateTime)
    actions = db.relationship(
        "Action",
        foreign_keys=[Action.username, Action.channel_id],
        backref="subscription",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    subscription_tags = db.relationship(
        "SubscriptionTag",
        foreign_keys=[SubscriptionTag.username, SubscriptionTag.channel_id],
        backref=db.backref("subscription", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return "<Subscription: {} subscribe to {}>".format(
            self.username, self.channel_id
        )

    def add_action(self, action_name, action_type, details):
        from . import Action

        return Action(action_name, action_type, self.user, self.channel, details)

    def remove_action(self, action_id):
        action = self.actions.filter_by(id=action_id).first()
        if action:
            db.session.delete(action)
            db.session.commit()
            return True
        return False

    def edit_action():
        pass
