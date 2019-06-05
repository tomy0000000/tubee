"""Channel Model"""
import urllib
from datetime import datetime

from flask import url_for, current_app
from .. import db
from ..helper.hub import subscribe, unsubscribe, details
from ..helper.youtube import build_service

class Channel(db.Model):
    __tablename__ = "channel"
    channel_id = db.Column(db.String(30), primary_key=True)
    channel_name = db.Column(db.String(100))
    thumbnails_url = db.Column(db.String(200))
    country = db.Column(db.String(5))
    language = db.Column(db.String(5))
    custom_url = db.Column(db.String(100))
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, nullable=False)
    latest_status = db.Column(db.String(20))
    expire_datetime = db.Column(db.DateTime)
    hub_infos = db.Column(db.JSON)
    renew_datetime = db.Column(db.DateTime)
    subscribe_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"))
    unsubscribe_datetime = db.Column(db.DateTime)
    subscribers = db.relationship("UserSubscription",
                                  foreign_keys="UserSubscription.subscribing_channel_id",
                                  backref=db.backref("channel", lazy="joined"),
                                  lazy="dynamic",
                                  cascade="all, delete-orphan")
    def __init__(self, channel_id):
        service = build_service()
        self.channel_id = channel_id
        self.channel_name = service.channels().list(
            part="snippet",
            id=channel_id
        ).execute()["items"][0]["snippet"]["title"]
        self.activate_response = self.activate()

    def __repr__(self):
        return "<channel {}(#{})>".format(self.channel_name, self.channel_id)

    def activate(self):
        """Submitting Hub Subscription"""
        callback_url = url_for("channel.callback", channel_id=self.channel_id, _external=True)
        param_query = urllib.parse.urlencode({"channel_id": self.channel_id})
        topic_url = current_app.config["HUB_YOUTUBE_TOPIC"] + param_query
        response = subscribe(callback_url, topic_url)
        if response.success:
            self.active = True
            self.subscribe_datetime = datetime.now()
            self.renew_datetime = datetime.now()
            db.session.commit()
        return response

    def deactivate(self):
        """Submitting Hub Unsubscription"""
        callback_url = url_for("channel.callback", channel_id=self.channel_id, _external=True)
        param_query = urllib.parse.urlencode({"channel_id": self.channel_id})
        topic_url = current_app.config["HUB_YOUTUBE_TOPIC"] + param_query
        response = unsubscribe(callback_url, topic_url)
        if response.success:
            self.active = False
            self.unsubscribe_datetime = datetime.now()
            db.session.commit()
        return response

    def get_hub_details(self, stringify=False):
        callback_url = url_for("channel.callback", channel_id=self.channel_id, _external=True)
        param_query = urllib.parse.urlencode({"channel_id": self.channel_id})
        topic_url = current_app.config["HUB_YOUTUBE_TOPIC"] + param_query
        response = details(callback_url, topic_url)
        self.latest_status = response["state"]
        self.expire_datetime = response["expiration"]
        if not stringify:
            response_copy = response.copy()
        response.pop("requests_url")
        response.pop("response_object")
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

    def renew_info(self):
        service = build_service()
        retrieved_infos = service.channels().list(
            part="snippet",
            id=self.channel_id
        ).execute()["items"][0]
        modification = {
            "channel_name": True,
            "thumbnails_url": True,
            "country": False,
            "defaultLanguage": False,
            "customUrl": False
        }
        self.channel_name = retrieved_infos["snippet"]["title"]
        self.thumbnails_url = retrieved_infos["snippet"]["thumbnails"]["high"]["url"]
        if "country" in retrieved_infos["snippet"]:
            self.country = retrieved_infos["snippet"]["country"]
            modification["country"] = True
        if "defaultLanguage" in retrieved_infos["snippet"]:
            self.language = retrieved_infos["snippet"]["defaultLanguage"]
            modification["defaultLanguage"] = True
        if "customUrl" in retrieved_infos["snippet"]:
            self.custom_url = retrieved_infos["snippet"]["customUrl"]
            modification["customUrl"] = True
        db.session.commit()
        # Consider adding localized infos(?)
        return modification

    def renew_hub(self):
        """Renew Subscription by submitting new Hub Subscription"""
        callback_url = url_for("channel.callback", channel_id=self.channel_id, _external=True)
        param_query = urllib.parse.urlencode({"channel_id": self.channel_id})
        topic_url = current_app.config["HUB_YOUTUBE_TOPIC"] + param_query
        response = subscribe(callback_url, topic_url)
        current_app.logger.info("Callback URL: {}".format(callback_url))
        current_app.logger.info("Topic URL   : {}".format(topic_url))
        current_app.logger.info("Channel ID  : {}".format(self.channel_id))
        current_app.logger.info("Response    : {}".format(response.status_code))
        if response.success:
            self.renew_datetime = datetime.now()
            db.session.commit()
        return response.success

    def renew(self):
        response = self.renew_info()
        hub = self.renew_hub()
        response["hub"] = hub
        return response
