"""Notification Model"""
from datetime import datetime
from flask import current_app
from .. import db, helper

class Notification(db.Model):
    """
    id              a unique id for identification
    initiator       which function/action fired this notification
    send_datetime   dt when this notification fired
    message         content of the notification
    response        recieved resopnse from Pushover Server
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
        self.id = helper.generate_random_id()
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
