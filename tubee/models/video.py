"""Video Model"""
from urllib.parse import urljoin

from dateutil import parser

from .. import db
from ..utils.youtube import build_youtube_api


class Video(db.Model):
    """Videos of Subscribed Channel"""

    __tablename__ = "video"
    id = db.Column(db.String(16), primary_key=True)
    name = db.Column(db.String(128))
    channel_id = db.Column(db.String(32), db.ForeignKey("channel.id"))
    uploaded_timestamp = db.Column(db.DateTime)
    details = db.Column(db.JSON, nullable=False, default={})
    channel = db.relationship("Channel", back_populates="videos")
    callbacks = db.relationship(
        "Callback", back_populates="video", lazy="dynamic", cascade="all, delete-orphan"
    )
    DETAILS_FIELDS = (
        "kind,etag,nextPageToken,prevPageToken,pageInfo,items(id,etag,"
        "snippet(publishedAt,channelId,title,description,"
        "thumbnails(default,medium,high,standard,maxres),"
        "channelTitle,liveBroadcastContent))"
    )
    THUMBNAIL_SIZES_TUPLE = [
        ("medium", "mqdefault.jpg", 320, 180),
        ("high", "hqdefault.jpg", 480, 360),
        ("standard", "sddefault.jpg", 640, 480),
        ("maxres", "maxresdefault.jpg", 1280, 720),
    ]

    def __init__(self, video_id, channel, details=None, fetch_infos=True):
        self.id = video_id
        self.channel = channel
        db.session.add(self)
        db.session.commit()
        if details:
            self.details = details
            self._process_details()
        elif fetch_infos:
            self.update_infos()

    def __iter__(self):
        for key in ["id", "name", "channel_id", "uploaded_timestamp", "details"]:
            yield (key, getattr(self, key))

    @property
    def thumbnails(self):
        base_url = self.details["thumbnails"]["default"]["url"]
        for size, filename, width, height in self.THUMBNAIL_SIZES_TUPLE:
            if size not in self.details["thumbnails"]:
                self.details["thumbnails"][size] = {
                    "url": urljoin(base_url, filename),
                    "width": width,
                    "height": height,
                }
        return self.details["thumbnails"]

    @thumbnails.setter
    def thumbnails(self, thumbnails):
        raise ValueError("thumbnails can not be set")

    @thumbnails.deleter
    def thumbnails(self):
        raise ValueError("thumbnails can not be delete")

    def _process_details(self):
        self.name = self.details["title"]
        self.uploaded_timestamp = parser.parse(self.details["publishedAt"])
        db.session.commit()

    def update_infos(self):
        try:
            self.details = (
                build_youtube_api()
                .videos()
                .list(part="snippet", id=self.id, fields=Video.DETAILS_FIELDS)
                .execute()["items"][0]["snippet"]
            )
            self._process_details()
            return True
        # TODO: Parse API Error
        except Exception as error:
            return error
