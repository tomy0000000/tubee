"""Callback Model"""
from datetime import datetime
from flask import current_app

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
    channel_id = db.Column(db.String(32), db.ForeignKey("channel.id"))
    video_id = db.Column(db.String(32), db.ForeignKey("video.id"))
    channel = db.relationship("Channel", back_populates="callbacks")
    video = db.relationship("Video", back_populates="callbacks")

    def __init__(self, channel):
        self.channel = channel
        db.session.add(self)
        db.session.commit()
        current_app.logger.info(f"Callback <{self.id}>: Created")

    def __repr__(self):
        return f"<{self.channel_id}'s Callback {self.id}>"
