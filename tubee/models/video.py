"""Video Model"""
from .. import db


class Video(db.Model):
    """Videos of Subscribed Channel"""
    __tablename__ = "video"
    video_id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(100))
    channel_id = db.Column(db.String(30), db.ForeignKey("channel.channel_id"), nullable=False)
    channel = db.relationship("Channel", back_populates="videos")
    uploaded_datetime = db.Column(db.DateTime)
    details = db.Column(db.JSON)

    def __init__(self, channel_id, video_id):
        self.channel_id = channel_id
        self.video_id = video_id
        db.session.add(self)
        db.session.commit()

    def update_infos(self):
        # TODO
        return None
