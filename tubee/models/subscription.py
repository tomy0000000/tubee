"""Subscription Model"""
from datetime import datetime

from .. import db
from ..exceptions import InvalidAction
from .subscription_tag import SubscriptionTag
from .tag import Tag


class Subscription(db.Model):
    """Relationship between User and Channel"""

    __tablename__ = "subscription"
    username = db.Column(
        db.String(32), db.ForeignKey("user.username"), primary_key=True
    )
    channel_id = db.Column(db.String(32), db.ForeignKey("channel.id"), primary_key=True)
    subscribe_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    unsubscribe_timestamp = db.Column(db.DateTime)
    user = db.relationship("User", back_populates="subscriptions")
    channel = db.relationship("Channel", back_populates="subscriptions")
    _actions = db.relationship(
        "Action",
        back_populates="subscription",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    _subscription_tags = db.relationship(
        "SubscriptionTag",
        back_populates="subscription",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __init__(self, username, channel_id):
        self.username = username
        self.channel_id = channel_id
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<Subscription: {self.username} subscribe to {self.channel_id}>"

    @property
    def actions(self):
        return [
            action
            for subscription_tag in self._subscription_tags
            for action in subscription_tag.tag.actions
        ] + self._actions.all()

    @actions.setter
    def actions(self, actions):
        raise ValueError("Actions should be modify using instance methods")

    @actions.deleter
    def actions(self):
        raise ValueError("Actions should be modify using instance methods")

    @property
    def tags(self):
        return [subscription_tag.tag for subscription_tag in self._subscription_tags]

    @tags.setter
    def tags(self, actions):
        raise ValueError("Tags should be modify using instance methods")

    @tags.deleter
    def tags(self):
        raise ValueError("Tags should be modify using instance methods")

    def add_tag(self, tag_name):
        tag = Tag.query.filter_by(name=tag_name, username=self.username).first()
        if not tag:
            tag = Tag(self.username, tag_name)
        elif tag in self.tags:
            raise InvalidAction(f"Subscription is already tagged with {tag_name}")
        SubscriptionTag(self.username, self.channel_id, tag.id)
        return True

    def remove_tag(self, tag_name):
        tag = Tag.query.filter_by(name=tag_name, username=self.username).first()
        if not tag:
            raise InvalidAction(f"Subscription is not tagged with {tag_name}")
        db.session.delete(tag)
        db.session.commit()
        return True
