"""User Model"""
import requests
from flask import current_app
from flask_login import UserMixin
from .. import bcrypt, db, login_manager, oauth
from ..helper.youtube import build_credentials, build_service

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
    password_hash = db.Column(db.String(128), nullable=False)
    admin = db.Column(db.Boolean, server_default="0")
    pushover_key = db.Column(db.String(40))
    # language = db.Column(db.String(5))
    youtube_credentials = db.Column(db.JSON)
    # youtube_subscription = db.Column(db.JSON)
    line_notify_credentials = db.Column(db.String(50))
    subscriptions = db.relationship("UserSubscription",
                                    foreign_keys="UserSubscription.subscriber_username",
                                    backref=db.backref("subscriber", lazy="joined"),
                                    lazy="dynamic",
                                    cascade="all, delete-orphan")
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
        self.password_hash = bcrypt.generate_password_hash(password)
    def __init__(self, username, password, **kwargs):
        super(User, self).__init__(**kwargs)
        self.username = username
        self.password = password
    def __repr__(self):
        return "<user {}>".format(self.username)
    def promote_to_admin(self):
        self.admin = True
        db.session.commit()
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
        return bcrypt.check_password_hash(self.password_hash, password)
    # Channel Relation Method
    def is_subscribing(self, channel):
        """Check if User is subscribing to a channel"""
        from . import Channel
        if isinstance(channel, Channel):
            channel_id = channel.channel_id
        else:
            channel_id = channel
        return self.subscriptions.filter_by(subscribing_channel_id=channel_id).first() is not None
    def subscribe_to(self, channel):
        """Create Subscription Relationship"""
        from . import Channel
        if not isinstance(channel, Channel):
            channel = Channel.query.filter_by(channel_id=channel)
        if not self.is_subscribing(channel):
            from . import UserSubscription
            subscription = UserSubscription(subscribers=self, subscribing=channel)
            db.session.add(subscription)
            db.session.commit()
        return True
    def unbsubscribe_from(self, channel):
        """Delete Subscription Relationship"""
        from . import Channel
        if not isinstance(channel, Channel):
            channel = Channel.query.filter_by(channel_id=channel)
        if self.is_subscribing(channel):
            subscription = self.subscriptions.filter_by(channel_id=channel.channel_id).first()
            db.session.delete(subscription)
            db.session.commit()
        return True
    # YouTube Service Methods
    def youtube_init(self, credentials):
        self.youtube_credentials = credentials
        db.session.commit()
    def youtube_revoke(self):
        credentials = build_credentials(self.youtube_credentials)
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
        return build_credentials(self.youtube_credentials)
    def get_youtube_service(self):
        return build_service(self.youtube_credentials)
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
        service = build_service(self.youtube_credentials)
        return service.playlistItems().insert(body=resource, part="snippet").execute()
    # Notification
    def line_notify_init(self, credentials):
        self.line_notify_credentials = credentials
        db.session.commit()
    def get_line_notify_credentials(self):
        return dict(
            access_token=self.line_notify_credentials,
            token_type="bearer"
        )
    def line_notify_revoke(self):
        response = oauth.LineNotify.post("api/revoke")
        if response.status_code == 200:
            self.line_notify_credentials = ""
            db.session.commit()
            return True
        current_app.logger.info("Line Notify Revoke Failed for "+self.username)
        current_app.logger.info("Response: "+str(response.status_code))
        current_app.logger.info("Detail: ")
        current_app.logger.info(response.text)
        return response.text
    def send_notification(self, initiator, *args, **kwargs):
        from . import Notification
        new_notification = Notification(initiator, self, *args, **kwargs)
        db.session.add(new_notification)
        db.session.commit()
        return new_notification.response
