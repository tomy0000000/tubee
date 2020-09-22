"""Channel Model"""
from datetime import datetime

from .. import db
from ..helper import build_callback_url, build_topic_url, try_parse_datetime
from ..helper.hub import details, subscribe, unsubscribe
from ..helper.youtube import build_youtube_api
from ..exceptions import InvalidAction, APIError

from googleapiclient.errors import Error as YouTubeAPIError
from flask import current_app


class Channel(db.Model):
    __tablename__ = "channel"
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(128))
    active = db.Column(db.Boolean, default=False)
    infos = db.Column(db.JSON)
    hub_infos = db.Column(db.JSON)
    subscribe_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    unsubscribe_timestamp = db.Column(db.DateTime)
    videos = db.relationship("Video", backref="channel", lazy="dynamic")
    callbacks = db.relationship("Callback", backref="channel", lazy="dynamic")
    subscribers = db.relationship(
        "Subscription",
        backref=db.backref("channel", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __init__(self, channel_id):
        from ..tasks import (
            channels_update_hub_infos,
            channels_fetch_videos,
            renew_channels,
        )

        self.id = channel_id
        db.session.add(self)
        db.session.commit()
        try:
            self.update_youtube_infos()
        except (APIError, InvalidAction) as error:
            db.session.delete(self)
            db.session.commit()
            raise error

        channels_update_hub_infos.apply_async(
            args=[[channel_id]],
            countdown=60,
        )
        channels_fetch_videos.apply_async(args=[[channel_id]])
        renew_channels.apply_async(args=[[channel_id], 345600], countdown=345600)
        self.activate()

    def __repr__(self):
        return "<Channel {} (#{})>".format(self.name, self.id)

    @property
    def expiration(self):
        try:
            return try_parse_datetime(self.hub_infos["expiration"])
        except (TypeError, KeyError):
            return None

    @expiration.setter
    def expiration(self, expiration):
        raise ValueError("expiration can not be set")

    @expiration.deleter
    def expiration(self):
        raise ValueError("expiration can not be delete")

    def activate(self):
        """Submitting hub Subscription, called when first user subscribe"""
        if self.active:
            raise AttributeError("Channel is already active")
        results = self.subscribe()
        if results:
            self.active = True
            self.subscribe_timestamp = datetime.utcnow()
            db.session.commit()
        return results

    def deactivate(self, callback_url=None, topic_url=None):
        """Submitting hub unsubscription, called when last user unsubscribe"""
        if not self.active:
            raise AttributeError("Channel is already deactivate")
        if not callback_url:
            callback_url = build_callback_url(self.id)
        if not topic_url:
            topic_url = build_topic_url(self.id)
        response = unsubscribe(
            current_app.config["HUB_GOOGLE_HUB"], callback_url, topic_url
        )
        if response.success:
            self.active = False
            self.unsubscribe_timestamp = datetime.utcnow()
            db.session.commit()
        return response

    def update_hub_infos(self, callback_url=None, topic_url=None):
        """Update hub subscription details, called by task or app"""
        if not callback_url:
            callback_url = build_callback_url(self.id)
        if not topic_url:
            topic_url = build_topic_url(self.id)
        results = details(current_app.config["HUB_GOOGLE_HUB"], callback_url, topic_url)
        results.pop("requests_url")
        results.pop("response_object")
        response = results.copy()
        for key, val in results.items():
            if not val:
                continue
            if isinstance(val, datetime):
                results[key] = str(val)
            elif isinstance(val[0], datetime):
                results[key] = (str(val[0]), val[1])
        self.hub_infos = results
        db.session.commit()
        return response

    def update_youtube_infos(self):
        """Update YouTube metadata, called by task"""
        try:
            api_result = (
                build_youtube_api()
                .channels()
                .list(part="snippet", id=self.id)
                .execute()
            )
            if "items" not in api_result:
                if self.name is None:
                    raise InvalidAction(f"Channel {self.id} doesn't exists")
                raise APIError(
                    service="YouTube",
                    message=f"Unable to update channel <{self.id}> info",
                )
            self.infos = api_result["items"][0]
            self.name = self.infos["snippet"]["title"]
            db.session.commit()
            return self.infos
        except (YouTubeAPIError, KeyError) as error:
            # TODO: Parse API Error
            raise APIError(
                service="YouTube",
                message=str(error.args),
                error_type=error.__class__.__name__,
            )

    def fetch_videos(self):
        """Update videos, Called by task"""
        from .video import Video

        search = build_youtube_api().search()
        request = search.list(
            part="snippet",
            channelId=self.id,
            maxResults=50,
            order="date",
            type="video",
            fields=Video.DETAILS_FIELDS,
        )

        results = {"new_item_appended": 0, "video_ids": []}
        while request is not None:
            api_results = request.execute()
            for video in api_results["items"]:
                video_id = video["id"]["videoId"]
                if not Video.query.get(video_id):
                    Video(video_id, self, details=video["snippet"])
                    results["new_item_appended"] += 1
                    results["video_ids"].append(video_id)
            request = search.list_next(request, api_results)

        return results

    def subscribe(self, callback_url=None, topic_url=None):
        """Submitting hub Subscription, called by task or app"""
        if not callback_url:
            callback_url = build_callback_url(self.id)
        if not topic_url:
            topic_url = build_topic_url(self.id)
        response = subscribe(
            current_app.config["HUB_GOOGLE_HUB"], callback_url, topic_url
        )
        current_app.logger.info("Callback URL: {}".format(callback_url))
        current_app.logger.info("Topic URL   : {}".format(topic_url))
        current_app.logger.info("Channel ID  : {}".format(self.id))
        current_app.logger.info("Response    : {}".format(response.status_code))
        return response.success

    # TODO: DEPRECATE THIS
    def renew(self, stringify=False, callback_url=None, topic_url=None):
        """Trigger renew functions"""

        response = {
            "subscription_response": self.subscribe(callback_url, topic_url),
            "info_response": self.update_youtube_infos(),
            # "hub_response": self.update_hub_infos(stringify=stringify, callback_url, topic_url),
        }
        # update_channel_hub_infos.apply_async(self.id, callback_url, topic_url)
        current_app.logger.info("Channel Renewed: {}<{}>".format(self.name, self.id))
        return response
