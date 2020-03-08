"""User Model"""
import json
import requests
import dropbox
from apiclient.errors import HttpError
from flask import current_app
from flask_login import UserMixin
from google.oauth2.credentials import Credentials
from pushover_complete import PushoverAPI
from .. import bcrypt, db, login_manager, oauth
from ..helper import youtube
from ..exceptions import (
    BackendError,
    InvalidParameter,
    ServiceNotSet,
)
login_manager.login_view = "user.login"


@login_manager.user_loader
def load_user(user_id):
    """Internal function for user info accessing"""
    return User.query.get(user_id)


class User(UserMixin, db.Model):
    """
    username                username for identification (Max:30)
    password_hash           user's hashed login password
    admin                   user is Tubee Admin
    pushover_key            access key to Pushover Service
    youtube_credentials     access credentials to YouTube Service
    subscriptions           User's Subscription to YouTube Channels
    """
    __tablename__ = "user"
    username = db.Column(db.String(32), primary_key=True)
    _password_hash = db.Column(db.LargeBinary(128), nullable=False)
    _pushover_key = db.Column(db.String(40))
    admin = db.Column(db.Boolean, server_default="0")
    # language = db.Column(db.String(5))
    youtube_credentials = db.Column(db.JSON)
    # youtube_subscription = db.Column(db.JSON)
    line_notify_credentials = db.Column(db.String(50))
    # preferred_notification_service = db.Column(db.Enum(Service))
    dropbox_credentials = db.Column(db.JSON)
    subscriptions = db.relationship("Subscription",
                                    back_populates="subscriber",
                                    lazy="dynamic",
                                    cascade="all, delete-orphan")
    notifications = db.relationship("Notification",
                                    back_populates="user",
                                    lazy="dynamic",
                                    cascade="all, delete-orphan")

    #      #####
    #     #     # #        ##    ####   ####  #    # ###### ##### #    #  ####  #####
    #     #       #       #  #  #      #      ##  ## #        #   #    # #    # #    #
    #     #       #      #    #  ####   ####  # ## # #####    #   ###### #    # #    #
    #     #       #      ######      #      # #    # #        #   #    # #    # #    #
    #     #     # #      #    # #    # #    # #    # #        #   #    # #    # #    #
    #      #####  ###### #    #  ####   ####  #    # ######   #   #    #  ####  #####

    def __init__(self, username, password, **kwargs):
        super(User, self).__init__(**kwargs)
        self.username = username
        self.password = password
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<User: {}>".format(self.username)

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
        raise InvalidParameter("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        if len(password) < 6:
            raise InvalidParameter("Password must be longer than 6 characters")
        if len(password) > 30:
            raise InvalidParameter("Password must be shorter than 30 characters")
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
            ServiceNotSet -- Raised when user has not setup Pushover key yet.
        """
        if not self._pushover_key:
            raise ServiceNotSet("User has not setup Pushover key")
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
            InvalidParameter -- Raised when user gave an invalid user key
        """
        pusher = PushoverAPI(current_app.config["PUSHOVER_TOKEN"])
        response = pusher.validate(key)
        if response["status"] != 1:
            raise InvalidParameter("Invalid Pushover User Key")
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
            ServiceNotSet -- Raised when user has not authorized yet.
        """
        if not self.youtube_credentials:
            raise ServiceNotSet("User has not authorized YouTube access")
        return youtube.build_youtube_api(self.youtube_credentials)

    @youtube.setter
    def youtube(self, credentials):
        """YouTube Setter

        Validating credentials and save iff valid

        Arguments:
            credentials {google.oauth2.credentials.Credentials} -- User's YouTube Credentials

        Raises:
            InvalidParameter -- Raised when provided credentials is not valid
        """
        if not isinstance(credentials, Credentials) or not credentials.valid:
            raise InvalidParameter("Invalid Credentials")
        self.youtube_credentials = dict(
            token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_uri=credentials.token_uri,
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
            scopes=credentials.scopes)
        db.session.commit()

    @youtube.deleter
    def youtube(self):
        """YouTube Deleter

        This Method revoke credentials and delete after action is executed
        successfully.

        Raises:
            BackendError -- Raised when revoke encounter issue
                                (not necessarily failed)
        """
        response = requests.post(
            "https://oauth2.googleapis.com/revoke",
            params={"token": self.youtube_credentials["token"]},
            headers={"content-type": "application/x-www-form-urlencoded"})
        if response.status_code == 200:
            self.youtube_credentials = None
            db.session.commit()
            return
        error_description = response.json()["error_description"]
        if error_description == "Token expired or revoked":
            self.youtube_credentials = None
            db.session.commit()
            raise BackendError(error_description, "success")
        raise BackendError(error_description, "danger")

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
            ServiceNotSet -- Raised when user has not authorized yet.
        """
        if not self.dropbox_credentials:
            raise ServiceNotSet("User has not authorized Dropbox access")
        return dropbox.Dropbox(self.dropbox_credentials["access_token"])

    @dropbox.setter
    def dropbox(self, credentials):
        self.dropbox_credentials = dict(access_token=credentials.access_token,
                                        account_id=credentials.account_id,
                                        user_id=credentials.user_id,
                                        url_state=credentials.url_state)
        db.session.commit()

    @dropbox.deleter
    def dropbox(self):
        self.dropbox.auth_token_revoke()
        self.dropbox_credentials = None
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
        if not self.line_notify_credentials:
            raise ServiceNotSet("User has not authorized Line Notify access")
        return oauth.LineNotify

    @line_notify.setter
    def line_notify(self, credentials):
        self.line_notify_credentials = credentials
        db.session.commit()

    @line_notify.deleter
    def line_notify(self):
        response = self.line_notify.post("api/revoke")
        if response.status_code != 200 and response.status_code != 401:
            raise BackendError(response.text)
        self.line_notify_credentials = None
        db.session.commit()

    #     #     #                      #     #
    #     #     #  ####  ###### #####  ##   ## # #    # # #    #
    #     #     # #      #      #    # # # # # #  #  #  # ##   #
    #     #     #  ####  #####  #    # #  #  # #   ##   # # #  #
    #     #     #      # #      #####  #     # #   ##   # #  # #
    #     #     # #    # #      #   #  #     # #  #  #  # #   ##
    #      #####   ####  ###### #    # #     # # #    # # #    #

    """Flask-Login UserMixin Properties and Methods"""
    """https://flask-login.readthedocs.io/en/latest/#your-user-class"""

    @property
    def is_authenticated(self):
        """Used to authenticate access to @login_required views.

        Returns:
            bool -- Whether user is authenticated or not.
        """
        return True

    @property
    def is_active(self):
        """Whether this account is activated, not been suspended, or any
        condition that caused this account being rejected or not.
        (This function is required but not in use)

        Returns:
            bool -- Whether account is active or not.
        """
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        """Get user's ID

        Returns:
            unicode -- ID that uniquely identifies this user
        """
        return self.username

    #     #     #
    #     ##   ## #  ####   ####
    #     # # # # # #      #    #
    #     #  #  # #  ####  #
    #     #     # #      # #
    #     #     # # #    # #    #
    #     #     # #  ####   ####

    # YouTube Method
    def is_subscribing(self, channel):
        """Check if User is subscribing to a channel"""
        from . import Channel
        if isinstance(channel, Channel):
            channel_id = channel.channel_id
        else:
            channel_id = channel
        return self.subscriptions.filter_by(
            subscribing_channel_id=channel_id).first() is not None

    def subscribe_to(self, channel_id):
        """Create Subscription Relationship"""
        from . import Channel, Subscription
        channel = Channel.query.get(channel_id)
        if self.is_subscribing(channel):
            raise InvalidParameter("You've' already subscribed this channel")
        if not channel:
            channel = Channel(channel_id)
        subscription = Subscription(subscriber_username=self.username,
                                    subscribing_channel_id=channel.channel_id)
        db.session.add(subscription)
        db.session.commit()
        return True

    def unbsubscribe(self, channel_id):
        """Delete Subscription Relationship"""
        subscription = self.subscriptions.filter_by(
            subscribing_channel_id=channel_id).first()
        if not subscription:
            raise InvalidParameter("User {} hasn't subscribe to {}".format(
                self.username, channel_id))
        db.session.delete(subscription)
        db.session.commit()
        return True

    def insert_video_to_playlist(self,
                                 video_id,
                                 playlist_id="WL",
                                 position=None):
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
        try:
            return self.youtube.playlistItems().insert(
                part="snippet", body=resource).execute()
        except HttpError as error:
            error_message = json.loads(error.content)["error"]["message"]
            current_app.logger.error(
                "Faield to insert {} to {}'s playlist".format(
                    video_id, self.username))
            current_app.logger.error(error_message)
            raise BackendError(error_message)

    # Pushover, Line Notify Methods
    def send_notification(self, initiator, service, **kwargs):
        """Send notification to user

        Arguments:
            initiator {str} -- Action or reason that trigger this notification
            service {str or notification.Service} -- Service used to send notification
            **kwargs {dict} -- optional arguments passed to notification

        Returns:
            dict -- Reponse from notification service
        """
        from . import Notification
        ntf = Notification(initiator, self, service, **kwargs)
        return ntf.response
