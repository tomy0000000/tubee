"""Notification Model"""
import codecs
import os
from datetime import datetime
from .. import db, helper


class Notification(db.Model):
    """An Object which describe a Notification for a specific user

    [description]

    Extends:
        db.Model

    Variables:
        id {str} -- identifier of this notification
        initiator {str} -- function or task which fire this notification
        user_id {str} -- receiver's username
        user {models.user.User} -- receiver user object
        sent_datetime {datetime.datetime} -- datetime when this object is created
        message {str} -- notification body
        kwargs {dict} -- other miscs of this notification
        response {dict} -- server response when notification is sent
    """
    __tablename__ = "notification"
    id = db.Column(db.String(32), primary_key=True)
    initiator = db.Column(db.String(15), nullable=False)
    user_id = db.Column(db.String(30), db.ForeignKey("user.username"))
    user = db.relationship("User", backref="notifications")
    sent_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"))
    message = db.Column(db.String(2000), nullable=False)
    kwargs = db.Column(db.JSON)
    response = db.Column(db.JSON)

    def __init__(self, initiator, user, *args, **kwargs):
        """An Object which describe a Notification for a specific user

        [description]

        Arguments:
            initiator {str} -- function or task which fire this notification
            user {models.user.User} -- receiver user object
        """
        self.id = codecs.encode(os.urandom(16), "hex").decode()
        self.initiator = initiator
        self.user = user
        self.sent_datetime = datetime.now()
        self.message = args[0]
        self.kwargs = kwargs
        if not kwargs.pop("raw_init", False):
            self.response = helper.send_notification(user, *args, **kwargs)
        db.session.add(self)
        db.session.commit()
    def __repr__(self):
        return "<notification %r>" %self.id
    def send(self):
        """Aftermath sending"""
        if self.resopnse:
            raise RuntimeError("Notification has already sent")
        self.response = helper.send_notification(self.user, self.message, self.kwargs)
        db.session.commit()
