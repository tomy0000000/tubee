"""UserSubscription Model"""
from .. import db


class UserSubscription(db.Model):
    """Relationship of User and Subscription"""
    __tablename__ = "user-subscription"
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

    def __repr__(self):
        return "<UserSubscription: {} subscribe to {}>".format(
            self.subscriber_username, self.subscribing_channel_id)
