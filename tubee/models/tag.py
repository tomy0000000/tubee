"""Tag Model"""
from .. import db


class Tag(db.Model):
    """Tag for grouping subscriptions"""

    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), db.ForeignKey("user.username"), nullable=False)
    name = db.Column(db.String(64), index=True, nullable=False)
    subscriptions = db.relationship(
        "SubscriptionTag",
        backref=db.backref("tag", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __init__(self, username, tag_name):
        self.username = username
        self.name = tag_name
        db.session.add(self)
        db.session.commit()
