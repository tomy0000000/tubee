"""Video Model"""
from .. import db


class Video(db.Model):
    """Videos of Subscribed Channel"""
    __tablename__ = "video"
    id = db.Column(db.String(16), primary_key=True)
    name = db.Column(db.String(128))
    channel_id = db.Column(db.String(32), db.ForeignKey("channel.id"))
    uploaded_timestamp = db.Column(db.DateTime)
    details = db.Column(db.JSON)
    callbacks = db.relationship("Callback", backref="video", lazy="dynamic")

    def __init__(self, video_id, channel_id):
        self.id = video_id
        self.channel_id = channel_id
        db.session.add(self)
        db.session.commit()

    def update_infos(self):
        # TODO
        return None
