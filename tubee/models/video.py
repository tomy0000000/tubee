"""Video Model"""
from dataclasses import dataclass
from datetime import datetime
from typing import Union
from urllib.parse import urljoin

from .. import db
from ..utils.youtube import build_youtube_api, fetch_video_metadata


@dataclass
class Video(db.Model):  # type: ignore
    """Videos of Subscribed Channel"""

    id: str
    name: str
    channel_id: str
    uploaded_timestamp: datetime
    details: dict

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

    @property
    def video_file_url(self) -> Union[str, None]:
        if metadata := fetch_video_metadata(self.id):
            return metadata.get("url")

    def _process_details(self):
        from ..utils import try_parse_datetime

        self.name = self.details["title"]
        if timestamp := try_parse_datetime(self.details["publishedAt"]):
            self.uploaded_timestamp = timestamp
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
            return self
        # TODO: Parse API Error
        except Exception as error:
            raise error

    def execute_action(self, action_id):
        """Execute Action on Video"""
        from . import Action

        return Action.query.get_or_404(action_id, "Action not found").execute(
            video_id=self.id,
            video_title=self.name,
            video_description=self.details["description"],
            video_thumbnail=self.details["thumbnails"]["medium"]["url"],
            video_thumbnail_small=self.details["thumbnails"]["default"]["url"],
            video_file_url=self.video_file_url,
            channel_name=self.channel.name,
        )
