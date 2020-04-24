"""Channel Model"""
import logging
from datetime import datetime

from .. import db
from ..exceptions import OperationalError
from ..helper import build_callback_url, build_topic_url, try_parse_datetime
from ..helper.hub import details, subscribe, unsubscribe
from ..helper.youtube import build_youtube_api

from googleapiclient.errors import Error

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
    subscribers = db.relationship(
        "Subscription",
        backref=db.backref("channel", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __init__(self, channel_id):
        from ..tasks import channels_update_hub_infos, channels_fetch_videos

        self.id = channel_id
        # TODO: Validate Channel
        db.session.add(self)
        db.session.commit()
        self.update_infos()
        channels_update_hub_infos.apply_async(
            args=[(self.id, build_callback_url(self.id), build_topic_url(self.id),)]
        )
        channels_fetch_videos.apply_async(args=[[self.id]])
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
        if response:
            self.active = True
            db.session.commit()
        return response

    def deactivate(self, callback_url=None, topic_url=None):
        """Submitting Hub Unsubscription"""
        if not callback_url:
            callback_url = build_callback_url(self.id)
        if not topic_url:
            topic_url = build_topic_url(self.id)
        response = unsubscribe(callback_url, topic_url)
        if response.success:
            self.active = False
            self.unsubscribe_timestamp = datetime.utcnow()
            db.session.commit()
        return response

    def update_hub_infos(self, stringify=False, callback_url=None, topic_url=None):
        if not callback_url:
            callback_url = build_callback_url(self.id)
        if not topic_url:
            topic_url = build_topic_url(self.id)
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
            self.infos = (
                build_youtube_api()
                .channels()
                .list(part="snippet", id=self.id)
                .execute()["items"][0]
            )
            self.name = self.infos["snippet"]["title"]
            db.session.commit()
            return True
        # TODO: Parse API Error
        except Error as error:
            logging.error("(API) {}: {}".format(error.__class__.__name__))
            return str(error.args)

    def fetch_videos(self):
        from .video import Video

        nextPageToken = None
        videos = []
        # QuickConvert, not guaranteed
        uploaded_video_playlist_id = "UU{}".format(self.id[2:])
        while True:
            results = (
                build_youtube_api()
                .playlistItems()
                .list(
                    part="snippet",
                    maxResults=50,
                    pageToken=nextPageToken,
                    playlistId=uploaded_video_playlist_id,
                )
                .execute()
            )
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
            video_id = video["snippet"]["resourceId"]["videoId"]
            if not Video.query.get(video_id):
                Video(video_id, self, fetch_infos=False)

    def subscribe(self, callback_url=None, topic_url=None):
        """Renew Subscription by submitting new Hub Subscription"""
        if not callback_url:
            callback_url = build_callback_url(self.id)
        if not topic_url:
            topic_url = build_topic_url(self.id)
        response = subscribe(callback_url, topic_url)
        logging.info("Callback URL: {}".format(callback_url))
        logging.info("Topic URL   : {}".format(topic_url))
        logging.info("Channel ID  : {}".format(self.id))
        logging.info("Response    : {}".format(response.status_code))
        if response.success:
            self.renew_datetime = datetime.utcnow()
            db.session.commit()
        return response.success

    # TODO: DEPRECATE THIS
    def renew(self, stringify=False, callback_url=None, topic_url=None):
        """Trigger renew functions"""
        from ..tasks import channels_update_hub_infos

        response = {
            "subscription_response": self.subscribe(callback_url, topic_url),
            "info_response": self.update_infos(),
            # "hub_response": self.update_hub_infos(stringify=stringify, callback_url, topic_url),
        }
        # update_channel_hub_infos.apply_async(self.id, callback_url, topic_url)
        logging.info("Channel Renewed: {}<{}>".format(self.name, self.id))
        return response
