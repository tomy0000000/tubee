"""SubscriptionTag Model"""
from dataclasses import dataclass

from .. import db


@dataclass
class SubscriptionTag(db.Model):  # type: ignore
    """Relationship between Subscription and Tag"""

    username: str
    channel_id: str
    tag_id: int

    __tablename__ = "subscription_tag"
    username = db.Column(db.String(32), primary_key=True)
    channel_id = db.Column(db.String(32), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"), primary_key=True)
    __table_args__ = (
        db.ForeignKeyConstraint(
            [username, channel_id], ["subscription.username", "subscription.channel_id"]
        ),
        {},
    )
    subscription = db.relationship("Subscription", back_populates="_subscription_tags")
    tag = db.relationship("Tag", back_populates="subscription_tags")

    def __init__(self, username, channel_id, tag_id):
        self.username = username
        self.channel_id = channel_id
        self.tag_id = tag_id
        db.session.add(self)
        db.session.commit()
