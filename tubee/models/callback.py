"""Callback Model"""
from dataclasses import dataclass
from datetime import datetime

from loguru import logger

from .. import db


@dataclass
class Callback(db.Model):
    """
    id            Unique ID
    type          Challenge or Notification
    timestamp     The timestamp when this callback was received
    infos         Details of the request context
    """

    id: int
    type: str
    timestamp: datetime
    infos: dict
    channel_id: str
    video_id: str

    __tablename__ = "callback"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    infos = db.Column(db.JSON, nullable=False, default={})
    channel_id = db.Column(db.String(32), db.ForeignKey("channel.id"))
    video_id = db.Column(db.String(32), db.ForeignKey("video.id"))
    channel = db.relationship("Channel", back_populates="callbacks")
    video = db.relationship("Video", back_populates="callbacks")

    def __init__(self, channel):
        self.channel = channel
        db.session.add(self)
        db.session.commit()
        logger.info(f"Callback <{self.id}>: Created")

    def __repr__(self):
        return f"<{self.channel_id}'s Callback {self.id}>"

    def __iter__(self):
        FIELD = [
            "id",
            "type",
            "timestamp",
            "infos",
            "channel_id",
            "video_id",
        ]
        for f in FIELD:
            yield (f, getattr(self, f))
