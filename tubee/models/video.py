"""Video Model"""
from dateutil import parser
from .. import db
from ..helper.youtube import build_youtube_api


class Video(db.Model):
    """Videos of Subscribed Channel"""
    __tablename__ = "video"
    id = db.Column(db.String(16), primary_key=True)
    name = db.Column(db.String(128))
    channel_id = db.Column(db.String(32), db.ForeignKey("channel.id"))
    uploaded_timestamp = db.Column(db.DateTime)
    details = db.Column(db.JSON)
    callbacks = db.relationship("Callback", backref="video", lazy="dynamic")

    def __init__(self, video_id, channel, fetch_infos=True):
        self.id = video_id
        self.channel = channel
        if fetch_infos:
            self.update_infos()
        db.session.add(self)
        db.session.commit()

    def _process_details(self):
        self.name = self.details["snippet"]["title"]
        self.uploaded_timestamp = parser.parse(
            self.details["snippet"]["publishedAt"])

    def update_infos(self):
        try:
            self.details = build_youtube_api().videos().list(
                part="snippet", id=self.id).execute()["items"][0]
            self._process_details()
            return True
        # TODO: Parse API Error
        except Exception as error:
            return error
