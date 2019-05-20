"""Database Models of Tubee"""
import urllib
from datetime import datetime

import requests
from apiclient import discovery
from flask import url_for, current_app
from flask_login import UserMixin
from . import bcrypt, db, helper, login_manager
from .helper import hub

login_manager.login_view = "user.login"
@login_manager.user_loader
def load_user(user_id):
    """Internal function for user info accessing"""
    return User.query.get(user_id)

"""
sqlalchemy.schema.Column
    name
    type
    primary_key         bool                            False
    autoincrement       bool                            "Auto" (True For Single-Primary-Key-INTEGER-Column)
    server_default      "NULL", "CURRENT_TIMESTAMP"     None ("NULL")
    nullable            bool                            not primary_key (True)
    index               bool                            None (False)
    unique              bool                            None (False)
sqlalchemy.schema.ForeignKey
    column              Relationship Column Object or "Column.String"
    name
sqlalchemy.orm.relationship
    backref             backref object or related object property name
sqlalchemy.orm.query.Query
    https://docs.sqlalchemy.org/en/13/orm/query.html
"""

class UserSubscription(db.Model):
    """Relationship of User and Subscription"""
    __tablename__ = "user-subscription"
    subscriber_username = db.Column(db.String(30), db.ForeignKey("user.username"), primary_key=True)
    subscribing_channel_id = db.Column(db.String(30), db.ForeignKey("channel.channel_id"), primary_key=True)
    subscribe_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"))
    unsubscribe_datetime = db.Column(db.DateTime)
    tags = db.Column(db.PickleType)

class User(UserMixin, db.Model):
    """
    username                username for identification (Max:30)
    password                user's login password
    admin                   user is Tubee Admin
    pushover_key            access key to Pushover Service
    youtube_credentials     access credentials to YouTube Service
    subscriptions           User's Subscription to YouTube Channels
    """
    __tablename__ = "user"
    username = db.Column(db.String(30), primary_key=True)
    password = db.Column(db.String(70), nullable=False)
    admin = db.Column(db.Boolean, server_default="0")
    pushover_key = db.Column(db.String(40))
    youtube_credentials = db.Column(db.JSON)
    subscriptions = db.relationship("UserSubscription",
                                    foreign_keys="UserSubscription.subscriber_username",
                                    backref=db.backref("subscriber", lazy="joined"),
                                    lazy="dynamic",
                                    cascade="all, delete-orphan")
    def __init__(self, username, password):
        self.username = username
        if len(password) < 6:
            raise ValueError("Password must be longer than 6 characters")
        elif len(password) > 30:
            raise ValueError("Password must be shorter than 30 characters")
        self.password = bcrypt.generate_password_hash(password)
    def __repr__(self):
        return "<users %r>" %self.username
    def promote_to_admin(self):
        self.admin = True
    def setting_pushover_key(self, key):
        pass
    """UserMixin Methods"""
    # def is_authenticated(self):
    #     # TODO
    #     return None
    def is_active(self):
        # TODO
        return None
    def is_anonymous(self):
        # TODO
        return None
    def get_id(self):
        """Retrieve user's username"""
        return self.username
    def check_password(self, password):
        """Return True if provided password is valid to login"""
        return bcrypt.check_password_hash(self.password, password)
    # Channel Relation Method
    def is_subscribing(self, channel):
        return self.subscriptions.filter_by(subscribing_channel_id=channel.channel_id).first() is not None
    def subscribe_to(self, channel):
        if not self.is_subscribing(channel):
            new_subscribing = UserSubscription(subscribers=self, subscribing=channel)
            db.session.add(new_subscribing)
            db.session.commit()
    # YouTube Service Methods
    def youtube_init(self, credentials):
        self.youtube_credentials = credentials
        db.session.commit()
    def youtube_revoke(self):
        credentials = helper.build_youtube_credentials(self.youtube_credentials)
        response = requests.post("https://accounts.google.com/o/oauth2/revoke",
                                 params={"token": credentials.token},
                                 headers={"content-type": "application/x-www-form-urlencoded"})
        if response.status_code == 200:
            self.youtube_credentials = {}
            db.session.commit()
            return True
        current_app.logger.info("YouTube Revoke Failed for "+self.username)
        current_app.logger.info("Response: "+str(response.status_code))
        current_app.logger.info("Detail: ")
        current_app.logger.info(response.text)
        return response.text
    def get_youtube_credentials(self):
        return helper.build_youtube_credentials(self.youtube_credentials)
    def get_youtube_service(self):
        return helper.build_youtube_service(self.youtube_credentials)
    def insert_video_to_playlist(self, video_id, playlist_id="WL", position=None):
        resource = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                },
                "position": position
            }
        }
        youtube_service = helper.build_youtube_service(self.youtube_credentials)
        return youtube_service.playlistItems().insert(body=resource, part="snippet").execute()
    # Notification
    def send_notification(self, initiator, *args, **kwargs):
        new_notification = Notification(initiator, self, *args, **kwargs)
        db.session.add(new_notification)
        db.session.commit()
        return new_notification.response

class Channel(db.Model):
    __tablename__ = "channel"
    channel_id = db.Column(db.String(30), primary_key=True)
    channel_name = db.Column(db.String(100))
    thumbnails_url = db.Column(db.String(200))
    country = db.Column(db.String(5))
    language = db.Column(db.String(5))
    custom_url = db.Column(db.String(100))
    active = db.Column(db.Boolean, nullable=False, server_default=None, unique=False)
    # latest_status = db.Column(db.String(20), nullable=True, server_default=None, unique=False)
    # expire_datetime = db.Column(db.DateTime, nullable=True, server_default=None, unique=False)
    renew_datetime = db.Column(db.DateTime)
    subscribe_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"))
    unsubscribe_datetime = db.Column(db.DateTime)
    subscribers = db.relationship("UserSubscription",
                                  foreign_keys="UserSubscription.subscribing_channel_id",
                                  backref=db.backref("channel", lazy="joined"),
                                  lazy="dynamic",
                                  cascade="all, delete-orphan")
    def __init__(self, channel_id):
        YouTube_Service_Public = discovery.build(
            current_app.config["YOUTUBE_API_SERVICE_NAME"],
            current_app.config["YOUTUBE_API_VERSION"],
            cache_discovery=False,
            developerKey=current_app.config["YOUTUBE_API_DEVELOPER_KEY"])
        self.channel_id = channel_id
        self.channel_name = YouTube_Service_Public.channels().list(
            part="snippet",
            id=channel_id
        ).execute()["items"][0]["snippet"]["title"]
        self.activate_response = self.activate()

    def __repr__(self):
        return "<channel %r>" %self.channel_name

    def activate(self):
        """Submitting Hub Subscription"""
        callback_url = url_for("channel.callback", channel_id=self.channel_id, _external=True)
        param_query = urllib.parse.urlencode({"channel_id": self.channel_id})
        topic_url = current_app.config["HUB_YOUTUBE_TOPIC"] + param_query
        response = hub.subscribe(callback_url, topic_url)
        if response.success:
            self.active = True
            self.subscribe_datetime = datetime.now()
            self.renew_datetime = datetime.now()
        return response

    def deactivate(self):
        """Submitting Hub Unsubscription"""
        callback_url = url_for("channel.callback", channel_id=self.channel_id, _external=True)
        param_query = urllib.parse.urlencode({"channel_id": self.channel_id})
        topic_url = current_app.config["HUB_YOUTUBE_TOPIC"] + param_query
        response = hub.unsubscribe(callback_url, topic_url)
        if response.success:
            self.active = False
            self.unsubscribe_datetime = datetime.now()
        return response

    def get_hub_details(self):
        callback_url = url_for("channel.callback", channel_id=self.channel_id, _external=True)
        param_query = urllib.parse.urlencode({"channel_id": self.channel_id})
        topic_url = current_app.config["HUB_YOUTUBE_TOPIC"] + param_query
        response = hub.details(callback_url, topic_url)
        return response

    def renew_info(self):
        """Update Database Info from YouTube"""
        YouTube_Service_Public = discovery.build(
            current_app.config["YOUTUBE_API_SERVICE_NAME"],
            current_app.config["YOUTUBE_API_VERSION"],
            cache_discovery=False,
            developerKey=current_app.config["YOUTUBE_API_DEVELOPER_KEY"])
        retrieved_infos = YouTube_Service_Public.channels().list(
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
        response = hub.subscribe(callback_url, topic_url)
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

# class Video(db.Model):
#     """Videos of Subscribed Channel"""
#     __tablename__ = "video"
#     id = db.Column(db.String(32), nullable=False, primary_key=True)
#     uploaded_datetime = db.Column(db.DateTime, nullable=True, server_default=None, unique=False)
#     def __init__(self, arg):
#         self.arg = arg

class Callback(db.Model):
    """
    id                   a unique id for identification
    revieved_datetime    datetime when this callback was received
    method               Type of HTTP request, e.g. "GET", "POST".......etc..
    path                 Paths which receive this request
    arguments            a dict of arguments from GET requests
    data                 POST reqests body
    user_agent           Sender's Identity
    """
    __tablename__ = "callback"
    id = db.Column(db.String(32), primary_key=True)
    received_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"))
    channel_id = db.Column(db.String(30), nullable=False)
    action = db.Column(db.String(30))
    details = db.Column(db.String(20))
    method = db.Column(db.String(10))
    path = db.Column(db.String(100))
    arguments = db.Column(db.JSON)
    data = db.Column(db.Text)
    user_agent = db.Column(db.String(200))

    def __init__(self, channel_id, action, details, method, path, arguments, data, user_agent):
        self.id = helper.generate_random_id()
        self.channel_id = channel_id
        self.action = action
        self.details = details
        self.method = method
        self.path = path
        self.arguments = arguments
        self.data = data
        self.user_agent = user_agent
    def __repr__(self):
        return "<callback %r>" %self.id

class Notification(db.Model):
    """
    id              a unique id for identification
    initiator       which function/action fired this notification
    send_datetime   dt when this notification fired
    message         content of the notification
    response        recieved resopnse from Pushover Server
    """
    __tablename__ = "notification"
    id = db.Column(db.String(32), primary_key=True)
    initiator = db.Column(db.String(15), nullable=False)
    user_id = db.Column(db.String(30), db.ForeignKey("user.username"))
    user = db.relationship("User", backref="notifications")
    sent_datetime = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"))
    message = db.Column(db.String(2000), nullable=False)
    kwargs = db.Column(db.JSON)
    response = db.Column(db.JSON)
    def __init__(self, initiator, user, *args, **kwargs):
        self.id = helper.generate_random_id()
        self.initiator = initiator
        self.user = user
        self.sent_datetime = datetime.now()
        self.message = args[0]
        self.kwargs = kwargs
        if not kwargs.pop("raw_init", False):
            current_app.logger.info(args)
            current_app.logger.info(kwargs)
            self.response = helper.new_send_notification(user, *args, **kwargs)
        db.session.add(self)
        db.session.commit()
    def __repr__(self):
        return "<notification %r>" %self.id
    def send(self):
        """Aftermath sending"""
        if self.resopnse:
            raise RuntimeError("Notification has already sent")
        self.response = helper.new_send_notification(self.user, self.message, self.kwargs)
        db.session.commit()

class APShedulerJobs(db.Model):
    """A Dummy Model for Flask Migrate"""
    __tablename__ = "apscheduler_jobs"
    id = db.Column(db.String(32), nullable=False, primary_key=True)
    next_run_time = db.Column(db.Float(64), index=True)
    job_state = db.Column(db.LargeBinary, nullable=False)
