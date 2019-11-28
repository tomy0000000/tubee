"""User Model"""
import requests
from flask import current_app
from flask_login import UserMixin
from google.oauth2.credentials import Credentials
from .. import bcrypt, db, login_manager, oauth
from ..helper import dropbox, youtube
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
    dropbox_credentials = db.Column(db.JSON)
    subscriptions = db.relationship("Subscription",
                                    back_populates="subscriber",
                                    lazy="dynamic",
                                    cascade="all, delete-orphan")

    @property
    def password(self):
        """Password Property"""
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        if len(password) < 6:
            raise ValueError("Password must be longer than 6 characters")
        if len(password) > 30:
            raise ValueError("Password must be shorter than 30 characters")
        self._password_hash = bcrypt.generate_password_hash(password)

    @property
    def pushover(self):
        """Pushover Key

        Returns:
            str -- User's Pushover Key

        Raises:
            AttributeError -- Raised when user has not setup Pushover key yet.
        """
        if not self._pushover_key:
            raise AttributeError("User has not setup Pushover key")
        return self._pushover_key

    @pushover.setter
    def pushover(self, key):
        """Pushover Setter

        Validating Key and save iff valid

        Arguments:
            key {str} -- User's pushover key obtain from https://pushover.net
        """
        # TODO: Implement Validating Function
        self._pushover_key = key
        db.session.commit()

    @pushover.deleter
    def pushover(self):
        """Pushover Deleter

        Remove Key
        """
        del self._pushover_key
        db.session.commit()

    @property
    def youtube(self):
        """YouTube Service

        build service with user's saved credentials.

        Returns:
            googleapiclient.discovery.Resource -- API-calling-ready YouTube Service

        Raises:
            AttributeError -- Raised when user has not authorized yet.
        """
        if not self.youtube_credentials:
            raise AttributeError("User has not authorized YouTube access")
        return youtube.build_service(self.youtube_credentials)

    @youtube.setter
    def youtube(self, credentials):
        """YouTube Setter

        Validating credentials and save iff valid

        Arguments:
            credentials {google.oauth2.credentials.Credentials} -- User's YouTube Credentials

        Raises:
            TypeError -- Raised when provided credentials is not a valid type.
            ValueError -- Raised when provided credentials is not valid.
        """
        if not isinstance(credentials, Credentials):
            raise TypeError("Invalid Type")
        if not credentials.valid:
            raise ValueError("Credentials is invalid")
        self.youtube_credentials = dict(
            token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_uri=credentials.token_uri,
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
            scopes=credentials.scopes
        )
        db.session.commit()

    @youtube.deleter
    def youtube(self):
        """YouTube Deleter

        This Method revoke credentials and delete after action is executed
        successfully.

        Raises:
            RuntimeError -- Raised when revoke failed to complete.
        """
        response = requests.post(
            "https://accounts.google.com/o/oauth2/revoke",
            params={"token": self.youtube_credentials["token"]},
            headers={"content-type": "application/x-www-form-urlencoded"})
        if response.status_code != 200:
            raise RuntimeError(response.text)
        del self.youtube_credentials
        db.session.commit()

    @property
    def dropbox(self):
        """Dropbox Service

        [description]

        Returns:
            [type] -- [description]

        Raises:
            AttributeError -- Raised when user has not authorized yet.
        """
        if not self.dropbox_credentials:
            raise AttributeError("User has not authorized Dropbox access")
        return dropbox.build_service(self.dropbox_credentials)

    @dropbox.setter
    def dropbox(self, credentials):
        self.dropbox_credentials = credentials
        db.session.commit()

    @dropbox.deleter
    def dropbox(self):
        self.dropbox.auth_token_revoke()
        del self.dropbox_credentials
        db.session.commit()

    @property
    def line_notify(self):
        pass

    @line_notify.setter
    def line_notify(self, credentials):
        self.line_notify_credentials = credentials
        db.session.commit()

    @line_notify.deleter
    def line_notify(self):
        response = oauth.LineNotify.post("api/revoke")
        if response.status_code != 200:
            raise RuntimeError(response.text)
        del self.line_notify_credentials
        db.session.commit()

    def line_notify_init(self, credentials):
        self.line_notify_credentials = credentials
        db.session.commit()

    def get_line_notify_credentials(self):
        return dict(access_token=self.line_notify_credentials,
                    token_type="bearer")

    def __init__(self, username, password, **kwargs):
        super(User, self).__init__(**kwargs)
        self.username = username
        self.password = password

    def __repr__(self):
        return "<User: {}>".format(self.username)

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

    def check_password(self, password):
        """Return True if provided password is valid to login"""
        return bcrypt.check_password_hash(self._password_hash, password)

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

    def subscribe_to(self, channel):
        """Create Subscription Relationship"""
        from . import Channel
        if not isinstance(channel, Channel):
            channel = Channel.query.filter_by(channel_id=channel)
        if not self.is_subscribing(channel):
            from . import Subscription
            subscription = Subscription(
                subscriber_username=self.username,
                subscribing_channel_id=channel.channel_id)
            db.session.add(subscription)
            db.session.commit()
        return True

    def unbsubscribe_from(self, channel):
        """Delete Subscription Relationship"""
        from . import Channel
        if not isinstance(channel, Channel):
            current_app.logger.info("Convert Channel")
            current_app.logger.info(channel)
            channel = Channel.query.filter_by(channel_id=channel).first()
        subscription = self.subscriptions.filter_by(
            subscribing_channel_id=channel.channel_id).first()
        if subscription:
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
        return self.youtube.playlistItems().insert(body=resource,
                                                   part="snippet").execute()

    # Pushover, Line Notify Methods
    def send_notification(self, initiator, **kwargs):
        from . import Notification, Service
        ntf = Notification(initiator, self, Service.PUSHOVER, **kwargs)
        return ntf.response

    # Dropbox Methods
    def save_file_to_dropbox(self, file_path):
        return dropbox.save_file_to_dropbox(self, file_path)

    def save_url_to_dropbox(self, url, filename):
        return dropbox.save_url_to_dropbox(self, url, filename)
