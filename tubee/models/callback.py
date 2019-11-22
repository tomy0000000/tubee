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
    channel = db.relationship("Channel", backref="videos")
    action = db.Column(db.String(30))
    details = db.Column(db.String(20))
    method = db.Column(db.String(10))
    path = db.Column(db.String(100))
    arguments = db.Column(db.JSON)
    data = db.Column(db.Text)
    user_agent = db.Column(db.String(200))

    def __init__(self, channel, action, details, method, path, arguments, data,
                 user_agent):
        self.callback_id = str(uuid4())
        self.channel = channel
        self.action = action
        self.details = details
        self.method = method
        self.path = path
        self.arguments = arguments
        self.data = data
        self.user_agent = user_agent

    def __repr__(self):
        return "<callback %r>" % self.callback_id
