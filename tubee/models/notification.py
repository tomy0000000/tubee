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
    user = db.relationship("User", backref="notifications")
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
        """
        self.notification_id = str(uuid4())
        self.initiator = initiator
        self.user = user
        self.service = service
        self.message = kwargs.pop("message", None)
        self.kwargs = kwargs
        db.session.add(self)
        db.session.commit()
        if self.sendable and send:
            self.send()

    def __repr__(self):
        return "<Notification: {}'s notification send with {}>".format(
            self.user.username, self.initiator)

    def sendable(self, alert=False):
        """Check if this object can be send

        Keyword Arguments:
            alert {bool} -- raise error when notification can not be send (default: {False})

        Returns:
            bool -- Whether Notification can be send

        Raises:
            RuntimeError -- Details of why notification can't be send (raise only when alert=True)
        """
        if not self.service:
            if alert:
                raise RuntimeError("Service is not set")
            return False
        if not self.message:
            if alert:
                raise RuntimeError("Message is empty")
            return False
        if self.sent_datetime:
            if alert:
                raise RuntimeError("This Notification has already sent")
            return False
        return True

    def send(self):
        """Trigger Sending with the service assigned

        Returns:
            dict -- Response from service

        Raises:
            RuntimeError -- Description of why notification is unsentable
        """
        self.sendable(alert=True)
        if self.service is Service.ALL or self.service is Service.PUSHOVER:
            return self._send_with_pushover()
        if self.service is Service.ALL or self.service == Service.LINE_NOTIFY:
            return self._send_with_line_notify()
        raise RuntimeError(
            "Notification is sendable, but something went wrong")

    def _send_with_pushover(self):
        """Send Notification with Pushover API

        Returns:
            dict -- Response from service
        """
        img_url = self.kwargs.pop("image")
        if img_url:
            img = requests.get(img_url, stream=True).content
        pusher = PushoverAPI(current_app.config["PUSHOVER_TOKEN"])
        self.resopnse = pusher.send_message(self.user.pushover,
                                            self.message,
                                            image=img,
                                            **self.kwargs)
        self.sent_datetime = datetime.now()
        db.session.commit()
        return self.response

    def _send_with_line_notify(self):
        """Send Notification with Line Notify API

        Returns:
            dict -- Response from service
        """
        # TODO: Move Line Notify Function to here
        pass
