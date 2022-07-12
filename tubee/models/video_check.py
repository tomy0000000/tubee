from dataclasses import dataclass

from .. import db


@dataclass
class VideoCheck(db.Model):
    """Label indicate if user had checked video"""

    username: str
    video_id: str
    checked: bool

    __tablename__ = "video_check"
    username = db.Column(db.String(32), primary_key=True)
    video_id = db.Column(db.String(16), primary_key=True)
    checked = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, username, video_id, checked=True):
        self.username = username
        self.video_id = video_id
        self.checked = checked
        db.session.add(self)
        db.session.commit()
