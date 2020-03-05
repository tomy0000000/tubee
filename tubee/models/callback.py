"""Callback Model"""
from uuid import uuid4
from .. import db


class Callback(db.Model):
    """
    id                   a unique id for identification
    revieved_datetime    datetime when this callback was received
    method               Type of HTTP request, e.g. "GET", "POST".......etc..
    path                 Paths which receive this request
    arguments            a dict of arguments from GET requests
    data                 POST reqests body
    user_agent           Sender's Identity
    """
    __tablename__ = "callback"
    callback_id = db.Column(db.String(36), primary_key=True)
    received_datetime = db.Column(db.DateTime,
                                  server_default=db.text("CURRENT_TIMESTAMP"))
    channel_id = db.Column(db.String(30),
                           db.ForeignKey("channel.channel_id"),
                           nullable=False)
    channel = db.relationship("Channel", back_populates="callbacks")
    action = db.Column(db.String(30))
    details = db.Column(db.String(20))
    method = db.Column(db.String(10))
    path = db.Column(db.String(100))
    arguments = db.Column(db.JSON)
    data = db.Column(db.Text)
    user_agent = db.Column(db.String(200))

    def __init__(self, channel):
        self.callback_id = str(uuid4())
        self.channel = channel
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<Callback {}>".format(self.callback_id)
