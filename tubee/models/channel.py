"""Channel Model"""
import urllib
import pyrfc3339
from datetime import datetime, timedelta
from flask import current_app, request, url_for
from .. import db
from ..exceptions import OperationalError
from ..helper import try_parse_datetime
from ..helper.hub import subscribe, unsubscribe, details
from ..helper.youtube import build_youtube_api


class Channel(db.Model):
    __tablename__ = "channel"
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(128))
    active = db.Column(db.Boolean)
    infos = db.Column(db.JSON)
    hub_infos = db.Column(db.JSON)
    subscribe_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    unsubscribe_timestamp = db.Column(db.DateTime)
    videos = db.relationship("Video", backref="channel", lazy="dynamic")
    callbacks = db.relationship("Callback", backref="channel", lazy="dynamic")
    subscribers = db.relationship("Subscription",
                                  backref=db.backref("channel", lazy="joined"),
                                  lazy="dynamic",
                                  cascade="all, delete-orphan")

    def __init__(self, channel_id):
        self.id = channel_id
        # TODO: Validate Channel
        self.name = build_youtube_api().channels().list(
            part="snippet",
            id=channel_id).execute()["items"][0]["snippet"]["title"]
        db.session.add(self)
        db.session.commit()
        self.update_infos()
        self.update_hub_infos()
        self.activate()

    def __repr__(self):
        return "<Channel {}(#{})>".format(self.name, self.id)

    @property
    def expiration(self):
        return try_parse_datetime(self.hub_infos["expiration"])

    @expiration.setter
    def expiration(self, expiration):
        raise OperationalError("expiration can not be set")

    @expiration.deleter
    def expiration(self, exception):
        raise OperationalError("expiration can not be delete")

    def activate(self):
        """Activate Subscription"""
        response = self.subscribe()
        self.fetch_videos()
        if response:
            self.active = True
            db.session.commit()
        return response

    def deactivate(self):
        """Submitting Hub Unsubscription"""
        callback_url = url_for("channel.callback",
                               channel_id=self.id,
                               _external=True)
        if current_app.config["HUB_RECEIVE_DOMAIN"]:
            callback_url = callback_url.replace(
                request.host, current_app.config["HUB_RECEIVE_DOMAIN"])
        param_query = urllib.parse.urlencode({"channel_id": self.id})
        topic_url = current_app.config["HUB_YOUTUBE_TOPIC"] + param_query
        response = unsubscribe(callback_url, topic_url)
        if response.success:
            self.active = False
            self.unsubscribe_timestamp = datetime.utcnow()
            db.session.commit()
        return response

    def update_hub_infos(self, stringify=False):
        callback_url = url_for("channel.callback",
                               channel_id=self.id,
                               _external=True)
        if current_app.config["HUB_RECEIVE_DOMAIN"]:
            callback_url = callback_url.replace(
                request.host, current_app.config["HUB_RECEIVE_DOMAIN"])
        param_query = urllib.parse.urlencode({"channel_id": self.id})
        topic_url = current_app.config["HUB_YOUTUBE_TOPIC"] + param_query
        response = details(callback_url, topic_url)
        response.pop("requests_url")
        response.pop("response_object")
        if not stringify:
            response_copy = response.copy()
        for key, val in response.items():
            if not val:
                continue
            if isinstance(val, datetime):
                response[key] = str(val)
            elif isinstance(val[0], datetime):
                response[key] = (str(val[0]), val[1])
        if stringify:
            response_copy = response.copy()
        self.hub_infos = response
        db.session.commit()
        return response_copy

    def update_infos(self):
        try:
            self.infos = build_youtube_api().channels().list(
                part="snippet", id=self.id).execute()["items"][0]
            return True
        # TODO: Parse API Error
        except Exception as error:
            return error

    def fetch_videos(self):
        from .video import Video
        nextPageToken = None
        videos = []
        while True:
            results = build_youtube_api().playlistItems().list(
                part="snippet",
                maxResults=50,
                pageToken=nextPageToken,
                playlistId=self.id).execute()
            # results = build_youtube_api().search().list(
            #     part="snippet",
            #     channelId=self.id,
            #     maxResults=50,
            #     pageToken=nextPageToken,
            #     publishedAfter=pyrfc3339.generate(datetime.utcnow() -
            #                                       timedelta(days=365),
            #                                       accept_naive=True),
            #     type="video").execute()
            videos += results["items"]
            if "nextPageToken" in results:
                nextPageToken = results["nextPageToken"]
            else:
                break
        for video in videos:
            Video(video["id"]["videoId"], self, fetch_infos=False)

    def subscribe(self):
        """Renew Subscription by submitting new Hub Subscription"""
        callback_url = url_for("channel.callback",
                               channel_id=self.id,
                               _external=True,
                               _scheme="https")
        if current_app.config["HUB_RECEIVE_DOMAIN"]:
            callback_url = callback_url.replace(
                request.host, current_app.config["HUB_RECEIVE_DOMAIN"])
        param_query = urllib.parse.urlencode({"channel_id": self.id})
        topic_url = current_app.config["HUB_YOUTUBE_TOPIC"] + param_query
        response = subscribe(callback_url, topic_url)
        current_app.logger.info("Callback URL: {}".format(callback_url))
        current_app.logger.info("Topic URL   : {}".format(topic_url))
        current_app.logger.info("Channel ID  : {}".format(self.id))
        current_app.logger.info("Response    : {}".format(
            response.status_code))
        if response.success:
            self.renew_datetime = datetime.utcnow()
            db.session.commit()
        return response.success

    def renew(self, stringify=False):
        """Trigger renew functions"""
        subscription_response = self.subscribe()
        info_response = self.update_infos()
        hub_response = self.update_hub_infos(stringify=stringify)
        response = info_response.copy()
        current_app.logger.info("Channel Renewed: {}<{}>".format(
            self.name, self.channel_id))
        current_app.logger.info(response)
        response.update({"subscribe": subscription_response})
        response.update(hub_response)
        return response
