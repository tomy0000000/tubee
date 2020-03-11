"""Action Model"""
from enum import Enum
from .. import db


class ActionType(Enum):
    Notification = "Notification"
    Playlist = "Playlist"
    Download = "Download"


class Action(db.Model):
    """Action to Perform when new video uploaded"""
    __tablename__ = "action"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    type = db.Column(db.Enum(ActionType), nullable=False)
    details = db.Column(db.JSON)
    username = db.Column(db.String(32), db.ForeignKey("subscription.username"))
    channel_id = db.Column(db.String(32),
                           db.ForeignKey("subscription.channel_id"))
    __table_args__ = (db.ForeignKeyConstraint(
        [username, channel_id],
        ["subscription.username", "subscription.channel_id"]), {})

    def __init__(self, action_name, action_type, user, channel, details=None):
        self.name = action_name
        self.type = action_type if action_type is ActionType else ActionType(
            action_type)
        self.username = user.username
        self.channel_id = channel.id
        self.details = details
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<Action: {} associate with user {} for {}>".format(
            self.type, self.username, self.channel_id)

    @property
    def user(self):
        from . import User
        return User.query.get(self.username)

    @user.setter
    def user(self, user_id):
        raise AttributeError("User can't be modified")

    @property
    def channel(self):
        from . import Channel
        return Channel.query.get(self.channel_id)

    @channel.setter
    def channel(self, channel_id):
        raise AttributeError("Channel can't be modified")

    def execute(self, **parameters):
        if self.type is ActionType.Notification:
            return self.user.send_notification(
                "Action",
                self.details.get("service", None),
                message=self.details.get("message",
                                         "{video_title}").format(**parameters),
                title=self.details.get(
                    "title", "New from {channel_name}").format(**parameters),
                url=self.details.get(
                    "url",
                    "https://www.youtube.com/watch?v={video_id}").format(
                        **parameters),
                url_title=self.details.get(
                    "url_title", "{video_title}").format(**parameters),
                image_url=self.details.get(
                    "image_url", "{video_thumbnails}").format(**parameters))
        if self.type is ActionType.Playlist:
            return self.user.insert_video_to_playlist(
                parameters["video_id"],
                playlist_id=self.details.get("playlist_id", None),
                position=self.details.get("position", None))
        if self.type is ActionType.Download:
            return self.user.dropbox.files_save_url(
                self.details.get("file_path",
                                 "/{video_title}.mp4").format(**parameters),
                parameters["video_file_url"])
