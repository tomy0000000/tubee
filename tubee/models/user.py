"""User Model"""
import json
from dataclasses import dataclass

import dropbox
import requests
from flask import current_app
from flask_login import UserMixin
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from pushover_complete import PushoverAPI

from .. import bcrypt, db, login_manager, oauth
from ..exceptions import APIError, InvalidAction, ServiceNotAuth
from ..utils import youtube


@login_manager.user_loader
def load_user(username):
    """Internal function for user info accessing"""
    return User.query.get(username)


@dataclass
class User(UserMixin, db.Model):
    """
    username                username for identification (Max:30)
    password_hash           user's hashed login password
    admin                   user is Tubee Admin
    pushover_key            access key to Pushover Service
    youtube_credentials     access credentials to YouTube Service
    subscriptions           User's Subscription to YouTube Channels
    """

    username: str
    admin: bool

    __tablename__ = "user"
    username = db.Column(db.String(32), primary_key=True)
    _password_hash = db.Column(db.LargeBinary(128), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    _pushover_key = db.Column(db.String(32))
    _youtube_credentials = db.Column(db.JSON, nullable=False, default={})
    _line_notify_credentials = db.Column(db.String(64))
    _dropbox_credentials = db.Column(db.JSON, nullable=False, default={})
    notifications = db.relationship(
        "Notification",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    subscriptions = db.relationship(
        "Subscription",
        back_populates="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    tags = db.relationship(
        "Tag", back_populates="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    actions = db.relationship("Action", back_populates="user", lazy="dynamic")

    #      #####
    #     #     # #        ##    ####   ####  #    # ###### ##### #    #  ####  #####
    #     #       #       #  #  #      #      ##  ## #        #   #    # #    # #    #
    #     #       #      #    #  ####   ####  # ## # #####    #   ###### #    # #    #
    #     #       #      ######      #      # #    # #        #   #    # #    # #    #
    #     #     # #      #    # #    # #    # #    # #        #   #    # #    # #    #
    #      #####  ###### #    #  ####   ####  #    # ######   #   #    #  ####  #####

    def __init__(self, username, password, admin=False, **kwargs):
        self.username = username
        self.password = password
        self.admin = admin
        db.session.add(self)
        db.session.commit()
        current_app.logger.info(f"User <{self.username}>: Create")

    def __repr__(self):
        return f"<User: {self.username}>"

    #     ######
    #     #     #   ##    ####   ####  #    #  ####  #####  #####
    #     #     #  #  #  #      #      #    # #    # #    # #    #
    #     ######  #    #  ####   ####  #    # #    # #    # #    #
    #     #       ######      #      # # ## # #    # #####  #    #
    #     #       #    # #    # #    # ##  ## #    # #   #  #    #
    #     #       #    #  ####   ####  #    #  ####  #    # #####

    @property
    def password(self):
        """Password Property"""
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        if len(password) < 6:
            raise ValueError("Password must be longer than 6 characters")
        if len(password) > 30:
            raise ValueError("Password must be shorter than 30 characters")
        self._password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        """Return True if provided password is valid to login"""
        return bcrypt.check_password_hash(self._password_hash, password)

    #     ######
    #     #     # #    #  ####  #    #  ####  #    # ###### #####
    #     #     # #    # #      #    # #    # #    # #      #    #
    #     ######  #    #  ####  ###### #    # #    # #####  #    #
    #     #       #    #      # #    # #    # #    # #      #####
    #     #       #    # #    # #    # #    #  #  #  #      #   #
    #     #        ####   ####  #    #  ####    ##   ###### #    #

    @property
    def pushover(self):
        """Pushover Key

        Returns:
            str -- User's Pushover Key

        Raises:
            ServiceNotAuth -- Raised when user has not setup Pushover key yet.
        """
        if not self._pushover_key:
            raise ServiceNotAuth("Pushover")
        return self._pushover_key

    @pushover.setter
    def pushover(self, key):
        """Pushover Setter

        Validating Key and save iff valid

        Decorators:
            pushover.setter

        Arguments:
            key {str} -- User's pushover key obtain from https://pushover.net

        Raises:
            InvalidAction -- Raised when user gave an invalid user key
        """
        pusher = PushoverAPI(current_app.config["PUSHOVER_TOKEN"])
        response = pusher.validate(key)
        if response["status"] != 1:
            raise InvalidAction("Invalid Pushover User Key")
        self._pushover_key = key
        db.session.commit()

    @pushover.deleter
    def pushover(self):
        """Pushover Deleter

        Remove Key
        """
        self._pushover_key = None
        db.session.commit()

    #     #     #               #######
    #      #   #   ####  #    #    #    #    # #####  ######
    #       # #   #    # #    #    #    #    # #    # #
    #        #    #    # #    #    #    #    # #####  #####
    #        #    #    # #    #    #    #    # #    # #
    #        #    #    # #    #    #    #    # #    # #
    #        #     ####   ####     #     ####  #####  ######

    @property
    def youtube(self):
        """YouTube Service

        build service with user's saved credentials.

        Returns:
            googleapiclient.discovery.Resource -- API-calling-ready YouTube
                                                  Service

        Raises:
            ServiceNotAuth -- Raised when user has not authorized yet.
        """
        if not self._youtube_credentials:
            raise ServiceNotAuth("YouTube")
        return youtube.build_youtube_api(self._youtube_credentials)

    @youtube.setter
    def youtube(self, credentials):
        """YouTube Setter

        Validating credentials and save iff valid

        Arguments:
            credentials {google.oauth2.credentials.Credentials} -- User's YouTube
                                                                   Credentials

        Raises:
            InvalidAction -- Raised when provided credentials is not valid
        """
        if not isinstance(credentials, Credentials) or not credentials.valid:
            raise InvalidAction("Invalid Credentials")
        self._youtube_credentials = dict(
            token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_uri=credentials.token_uri,
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
            scopes=credentials.scopes,
        )
        db.session.commit()

    @youtube.deleter
    def youtube(self):
        """YouTube Deleter

        This Method revoke credentials and delete after action is executed
        successfully.

        Raises:
            APIError -- Raised when revoke encounter issue
                                (not necessarily failed)
        """
        response = requests.post(
            "https://oauth2.googleapis.com/revoke",
            params={"token": self._youtube_credentials["token"]},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
        if response.status_code == 200:
            self._youtube_credentials = None
            db.session.commit()
            return
        error_description = response.json()["error_description"]
        if error_description == "Token expired or revoked":
            self._youtube_credentials = None
            db.session.commit()
            raise APIError(service="YouTube", message=error_description)
        raise APIError(service="YouTube", message=error_description)

    #     ######
    #     #     # #####   ####  #####  #####   ####  #    #
    #     #     # #    # #    # #    # #    # #    #  #  #
    #     #     # #    # #    # #    # #####  #    #   ##
    #     #     # #####  #    # #####  #    # #    #   ##
    #     #     # #   #  #    # #      #    # #    #  #  #
    #     ######  #    #  ####  #      #####   ####  #    #

    @property
    def dropbox(self):
        """Dropbox Service

        [description]

        Returns:
            [type] -- [description]

        Raises:
            ServiceNotAuth -- Raised when user has not authorized yet.
        """
        if not self._dropbox_credentials:
            raise ServiceNotAuth("Dropbox")
        return dropbox.Dropbox(self._dropbox_credentials["access_token"])

    @dropbox.setter
    def dropbox(self, credentials):
        self._dropbox_credentials = dict(
            access_token=credentials.access_token,
            account_id=credentials.account_id,
            user_id=credentials.user_id,
            url_state=credentials.url_state,
        )
        db.session.commit()

    @dropbox.deleter
    def dropbox(self):
        self.dropbox.auth_token_revoke()
        self._dropbox_credentials = None
        db.session.commit()

    #     #                          #     #
    #     #       # #    # ######    ##    #  ####  ##### # ###### #   #
    #     #       # ##   # #         # #   # #    #   #   # #       # #
    #     #       # # #  # #####     #  #  # #    #   #   # #####    #
    #     #       # #  # # #         #   # # #    #   #   # #        #
    #     #       # #   ## #         #    ## #    #   #   # #        #
    #     ####### # #    # ######    #     #  ####    #   # #        #

    @property
    def line_notify(self):
        if not self._line_notify_credentials:
            raise ServiceNotAuth("Line Notify")
        return oauth.LineNotify

    @line_notify.setter
    def line_notify(self, credentials):
        self._line_notify_credentials = credentials
        db.session.commit()

    @line_notify.deleter
    def line_notify(self):
        response = self.line_notify.post("api/revoke")
        if response.status_code != 200 and response.status_code != 401:
            raise APIError(service="Line Notify", message=response.text)
        self._line_notify_credentials = None
        db.session.commit()

    #     #     #
    #     ##   ## #  ####   ####
    #     # # # # # #      #    #
    #     #  #  # #  ####  #
    #     #     # #      # #
    #     #     # # #    # #    #
    #     #     # #  ####   ####

    def get_id(self):
        """Get user's ID

        Returns:
            unicode -- ID that uniquely identifies this user
        """
        return self.username

    # Service Test Functions
    def pushover_configured(self):
        return bool(self._pushover_key)

    def youtube_configured(self):
        return bool(self._youtube_credentials)

    def dropbox_configured(self):
        return bool(self._dropbox_credentials)

    def line_notify_configured(self):
        return bool(self._line_notify_credentials)

    # YouTube Method
    def is_subscribing(self, channel):
        """Check if User is subscribing to a channel"""
        from . import Channel

        if isinstance(channel, Channel):
            channel_id = channel.id
        else:
            channel_id = channel
        return self.subscriptions.filter_by(channel_id=channel_id).first() is not None

    def subscribe(self, channel_id):
        """Create Subscription Relationship"""
        from . import Channel, Subscription

        if not channel_id:
            raise InvalidAction("Invalid Channel ID")
        channel = Channel.query.get(channel_id)
        if not channel:
            channel = Channel(channel_id)
        if self.is_subscribing(channel):
            raise InvalidAction("You've already subscribed this channel")
        Subscription(self.username, channel.id)
        current_app.logger.info(f"Subscription <{self.username}, {channel_id}>: Create")
        return True

    def unbsubscribe(self, channel_id):
        """Delete Subscription Relationship"""
        subscription = self.subscriptions.filter_by(channel_id=channel_id).first()
        if not subscription:
            raise InvalidAction(
                f"User {self.username} hasn't subscribe to {channel_id}"
            )
        db.session.delete(subscription)
        db.session.commit()
        current_app.logger.info(f"Subscription <{self.username}, {channel_id}>: Remove")
        return True

    def insert_video_to_playlist(self, video_id, playlist_id="WL", position=None):
        resource = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {"kind": "youtube#video", "videoId": video_id},
                "position": position,
            }
        }
        try:
            result = (
                self.youtube.playlistItems()
                .insert(part="snippet", body=resource)
                .execute()
            )
            current_app.logger.info(
                f"User <{self.username}>: "
                f"Insert video <{video_id}> to playlist <{playlist_id}>"
            )
            return result
        except HttpError as error:
            error_message = json.loads(error.content)["error"]["message"]
            current_app.logger.error(
                f"Faield to insert {video_id} to {self.username}'s playlist"
            )
            current_app.logger.error(error_message)
            raise APIError(service="YouTube", message=error_message)

    # Pushover, Line Notify Methods
    def send_notification(self, initiator, service, **kwargs):
        """Send notification to user

        Arguments:
            initiator {str} -- Action or reason that trigger this notification
            service {str or notification.Service} -- Service used to send notification
            **kwargs {dict} -- optional arguments passed to notification

        Returns:
            dict -- Response from notification service
        """
        from . import Notification

        ntf = Notification(initiator, self, service, **kwargs)
        return ntf.response

    def mark_video_as_checked(self, video_id):
        """Mark video as checked"""
        from . import Video, VideoCheck

        video = Video.query.get(video_id)
        if not video:
            raise InvalidAction(f"Video {video_id} doesn't exist")
        video_check = VideoCheck.query.get((self.username, video_id))
        if video_check:
            video_check.checked = True
            db.session.commit()
        else:
            video_check = VideoCheck(self.username, video_id)
        current_app.logger.info(
            f"User <{self.username}> marked Video <{video_id}> as checked"
        )
        return video_check
