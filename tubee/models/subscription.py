"""Subscription Model"""
from .. import db


class Subscription(db.Model):
    """Relationship of User and Subscription"""
    __tablename__ = "subscription"
    subscriber_username = db.Column(db.String(30),
                                    db.ForeignKey("user.username"),
                                    primary_key=True)
    subscribing_channel_id = db.Column(db.String(30),
                                       db.ForeignKey("channel.channel_id"),
                                       primary_key=True)
    subscribe_datetime = db.Column(db.DateTime,
                                   server_default=db.text("CURRENT_TIMESTAMP"))
    unsubscribe_datetime = db.Column(db.DateTime)
    tags = db.Column(db.PickleType)
    subscriber = db.relationship("User", back_populates="subscriptions")
    channel = db.relationship("Channel", back_populates="subscribers")
    actions = db.relationship("Action",
                              back_populates="subscription",
                              lazy="dynamic",
                              cascade="all, delete-orphan")

    def __repr__(self):
        return "<Subscription: {} subscribe to {}>".format(
            self.subscriber_username, self.subscribing_channel_id)

    def run_actions():
        pass

    def add_action():
        pass

    def remove_action():
        pass
