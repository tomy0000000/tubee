"""Notification Model"""
import requests
from enum import Enum
from datetime import datetime
from flask import current_app
from pushover_complete import PushoverAPI
from uuid import uuid4
from .. import db


class Service(Enum):
    ALL = "ALL"
    PUSHOVER = "Pushover"
    LINE_NOTIFY = "Line Notify"


VALID_ARGS = {
    Service.PUSHOVER: [
        "device", "title", "url", "url_title", "image_url", "priority",
        "retry", "expire", "callback_url", "timestamp", "sound", "html"
    ],
    Service.LINE_NOTIFY:
    ["image_url", "stickerPackageId", "stickerId", "notificationDisabled"]
}


class Notification(db.Model):
    """An Object which describe a Notification for a specific user

    Variables:
        id {str} -- identifier of this notification
        initiator {str} -- function or task which fire this notification
        user_id {str} -- receiver's username
        user {user.User} -- receiver user object
        service {notification.Service} -- service used to send notification
        message {str} -- notification body
        kwargs {dict} -- other miscs of this notification
        sent_datetime {datetime.datetime} -- datetime when this object is created
        response {dict} -- server response when notification is sent
    """
    __tablename__ = "notification"
    notification_id = db.Column(db.String(36), primary_key=True)
    initiator = db.Column(db.String(15), nullable=False)
    user_id = db.Column(db.String(30), db.ForeignKey("user.username"))
    user = db.relationship("User", back_populates="notifications")
    service = db.Column(db.Enum(Service))
    message = db.Column(db.String(2000))
    kwargs = db.Column(db.JSON)
    sent_datetime = db.Column(db.DateTime)
    response = db.Column(db.JSON)

    def __init__(self, initiator, user, service, send=True, **kwargs):
        """An Object which describe a Notification for a specific user

        Arguments:
            initiator {str} -- function or task which fire this notification
            user {user.User} -- receiver user object
            service {notification.Service} -- service used to send notification

        Keyword Arguments:
            send {bool} -- Send on initialize (default: {True})
            message {str} -- message of Notification
            image_url {str} -- URL of the image
        """
        self.notification_id = str(uuid4())
        self.initiator = initiator
        self.user = user
        self.service = service
        self.message = kwargs.pop("message", None)
        self.kwargs = kwargs
        db.session.add(self)
        db.session.commit()
        if send:
            self.send()

    def __repr__(self):
        return "<Notification: {}'s notification send with {}>".format(
            self.user.username, self.initiator)

    @staticmethod
    def _clean_up_kwargs(kwargs, service):
        for key, val in kwargs.items():
            if key not in VALID_ARGS[service]:
                current_app.logger.warning(
                    "Invalid {} Notification Arguments ({}, {}) is ommited".
                    format(service.value, key, val))
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
        if self.sent_datetime:
            raise AttributeError("This Notification has already sent")
        response = {}
        if self.service is Service.ALL or self.service is Service.PUSHOVER:
            response["Pushover"] = self._send_with_pushover()
        if self.service is Service.ALL or self.service == Service.LINE_NOTIFY:
            response["Line Notify"] = self._send_with_line_notify()
        self.resopnse = response
        self.sent_datetime = datetime.now()
        db.session.commit()
        return response

    def _send_with_pushover(self):
        """Send Notification with Pushover API

        Returns:
            dict -- Response from service
        """
        kwargs = Notification._clean_up_kwargs(self.kwargs.copy(),
                                               self.service)
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
        kwargs = Notification._clean_up_kwargs(self.kwargs.copy(),
                                               self.service)
        kwargs["imageFullsize"] = kwargs.pop("image_url", None)
        return self.user.line_notify.post("api/notify",
                                          data=dict(message=self.message,
                                                    **kwargs))
