"""Video Model"""
from .. import db

class Video(db.Model):
    """Videos of Subscribed Channel"""
    __tablename__ = "video"
    video_id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    channel_id = db.Column(db.String(30), db.ForeignKey("channel.channel_id"))
    channel = db.relationship("Channel", backref="videos")
    uploaded_datetime = db.Column(db.DateTime)
    thumbnails_url = db.Column(db.String(200))
    def __init__(self, video_id):
        self.video_id = video_id
    def update_infos(self):
        # TODO
        return None
