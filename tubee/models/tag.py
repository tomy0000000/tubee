"""Tag Model"""
from .. import db


class Tag(db.Model):
    """Tag for grouping subscriptions"""

    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, nullable=False)
    username = db.Column(db.String(32), db.ForeignKey("user.username"))
    subscriptions = db.relationship(
        "SubscriptionTag",
        backref=db.backref("tag", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
