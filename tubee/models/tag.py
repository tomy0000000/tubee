"""Tag Model"""
from dataclasses import dataclass

from loguru import logger

from .. import db


@dataclass
class Tag(db.Model):
    """Tag for grouping subscriptions"""

    id: int
    username: str
    name: str

    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), db.ForeignKey("user.username"), nullable=False)
    name = db.Column(db.String(64), index=True, nullable=False)
    user = db.relationship("User", back_populates="tags")
    subscription_tags = db.relationship(
        "SubscriptionTag",
        back_populates="tag",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    actions = db.relationship(
        "Action", back_populates="tag", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __init__(self, username, tag_name):
        self.username = username
        self.name = tag_name
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<{self.username}'s Tag: {self.name}>"

    def rename(self, new_name):
        """Rename the tag"""
        self.name = new_name
        db.session.commit()
        logger.info(f'Tag <{self.id}>: Rename to "{new_name}"')
        return self

    def delete(self):
        """Delete the tag"""
        tag_id = self.id
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info(f"Tag <{tag_id}>: Remove")
            return self
        except Exception as error:
            # TODO: not sure if this is the right way to handle this
            logger.exception(f"Tag <{tag_id}>: Remove failed")
            raise error
