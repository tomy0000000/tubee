"""Tag Model"""
from .. import db


class Tag(db.Model):
    """Tag for grouping subscriptions"""

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

    @property
    def form(self):
        from ..forms import TagForm

        return TagForm(hidden_mode=True)

    @form.setter
    def form(self, form):
        raise ValueError("Form can't be modify")

    @form.deleter
    def form(self):
        raise ValueError("Form can't be modify")

    def rename(self, new_name):
        """Rename the tag"""
        self.name = new_name
        db.session.commit()
