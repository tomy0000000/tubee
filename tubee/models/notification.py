"""Notification Model"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import requests
from flask import current_app
from loguru import logger
from pushover_complete import PushoverAPI

from .. import db
from ..exceptions import APIError


class Service(str, Enum):
    Pushover = "Pushover"
    LineNotify = "Line_Notify"


VALID_ARGS = {
    Service.Pushover: [
        "device",
        "title",
        "url",
        "url_title",
        "image_url",
        "priority",
        "retry",
        "expire",
        "callback_url",
        "timestamp",
        "sound",
        "html",
    ],
    Service.LineNotify: [
        "imageThumbnail",
        "imageFullsize",
        "stickerPackageId",
        "stickerId",
        "notificationDisabled",
    ],
}


@dataclass
class Notification(db.Model):  # type: ignore
    """An Object which describe a Notification for a specific user

    Variables:
        id {str} -- identifier of this notification
        initiator {str} -- function or task which fire this notification
        user_id {str} -- receiver's username
        user {user.User} -- receiver user object
        service {str} -- service used to send notification
        message {str} -- notification body
        kwargs {dict} -- other miscs of this notification
        sent_datetime {datetime.datetime} -- datetime when this object is created
        response {dict} -- server response when notification is sent
    """

    id: int
    initiator: str
    username: str
    service: Service
    message: str
    kwargs: dict
    sent_timestamp: datetime
    response: dict

    __tablename__ = "notification"
    id = db.Column(db.Integer, primary_key=True)
    initiator = db.Column(db.String(16), nullable=False)
    username = db.Column(db.String(32), db.ForeignKey("user.username"))
    service = db.Column(db.Enum(Service))
    message = db.Column(db.Text)
    kwargs = db.Column(db.JSON, nullable=False, default={})
    sent_timestamp = db.Column(db.DateTime, index=True)
    response = db.Column(db.JSON, nullable=False, default={})
    user = db.relationship("User", back_populates="notifications")

    def __init__(self, initiator, user, service, send=True, **kwargs):
        """An Object which describe a Notification for a specific user

        Arguments:
            initiator {str} -- function or task which fire this notification
            user {user.User} -- receiver user object
            service {str or notification.Service} -- service used to send notification

        Keyword Arguments:
            send {bool} -- Send on initialize (default: {True})
            message {str} -- message of Notification
            image_url {str} -- URL of the image
        """
        self.user = user
        self.service = Service(service)

        # This step validate that the user has authorized the service
        getattr(self.user, self.service.value.lower())

        self.initiator = initiator
        self.message = kwargs.pop("message", None)
        self.kwargs = kwargs
        db.session.add(self)
        db.session.commit()
        logger.info(f"Notification <{self.id}>: Create")
        if send:
            self.send()

    def __repr__(self):
        return f"<Notification <{self.id}>"

    @staticmethod
    def _clean_up_kwargs(kwargs, service):
        invalid_args = {
            key: val for key, val in kwargs.items() if key not in VALID_ARGS[service]
        }
        for key, val in invalid_args.items():
            logger.warning(f"Invalid argument ({key}, {val}) is ommited")
            kwargs.pop(key)
        return kwargs

    def send(self):
        """Trigger Sending with the service assigned

        Returns:
            dict -- Response from service

        Raises:
            AttributeError -- Description of why notification is unsentable
        """
        if not self.service:
            raise AttributeError("Service is not set")
        if not self.message:
            raise AttributeError("Message is empty")
        if self.sent_timestamp:
            raise AttributeError("This Notification has already sent")

        success = False
        if self.service is Service.Pushover:
            results = self._send_with_pushover()
            self.response = results
            success = results["status"] == 1
        if self.service is Service.LineNotify:
            results = self._send_with_line_notify()
            self.response = results.json()
            success = results.status_code == 200

        self.sent_timestamp = datetime.utcnow()
        db.session.commit()
        logger.info(f"Notification <{self.id}>: Sent")
        if not success:
            raise APIError(service=self.service)
        return self.response

    def _send_with_pushover(self):
        """Send Notification with Pushover API

        Returns:
            dict -- Response from service
        """
        kwargs = Notification._clean_up_kwargs(self.kwargs.copy(), self.service)
        image_url = kwargs.pop("image_url", None)
        if image_url:
            kwargs["image"] = requests.get(image_url, stream=True).content
        pusher = PushoverAPI(current_app.config["PUSHOVER_TOKEN"])
        return pusher.send_message(self.user.pushover, self.message, **kwargs)

    def _send_with_line_notify(self):
        """Send Notification with Line Notify API

        Returns:
            dict -- Response from service
        """
        kwargs = self.kwargs.copy()
        kwargs["imageThumbnail"] = kwargs.pop("video_thumbnail_small", None)
        kwargs["imageFullsize"] = kwargs.pop("video_thumbnail", None)
        self.kwargs = Notification._clean_up_kwargs(kwargs, self.service)
        return self.user.line_notify.post(
            "api/notify", data=dict(message=self.message, **self.kwargs)
        )
