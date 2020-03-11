"""Callback Model"""
from datetime import datetime
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
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    infos = db.Column(db.JSON)
    channel_id = db.Column(db.String(32),
                           db.ForeignKey("channel.id"))
    video_id = db.Column(db.String(32),
                         db.ForeignKey("video.id"))

    def __init__(self, channel):
        self.callback_id = str(uuid4())
        self.channel = channel
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<{}'s Callback {}>".format(self.channel_id, self.callback_id)
