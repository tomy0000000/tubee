"""Callback Model"""
from datetime import datetime

from flask import current_app

from .. import db


class Callback(db.Model):
    """
    id            Unique ID
    type          Challenge or Notification
    timestamp     The timestamp when this callback was received
    infos         Details of the request context
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
