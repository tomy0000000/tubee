"""Helper Functions"""
from functools import wraps
import requests
import pushover_complete
from flask import abort, current_app
from flask_login import current_user
from ..models.user import User


def admin_required(func):
    """Restrict view function to admin-only"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.admin:
            abort(403)
        return func(*args, **kwargs)
    return decorated_function


def youtube_required(func):
    """Check if user has authenticated youtube access"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.youtube:
            abort(403)
        return func(*args, **kwargs)
    return decorated_function


def notify_admin(initiator, **kwargs):
    """Send Notification to all Admin with pushover set"""
    admins = User.query.filter_by(admin=True).all()
    response = {}
    for admin in admins:
        if admin.pushover:
            response[admin.username] = admin.send_notification(initiator, **kwargs)
    return response


def send_notification(user, *args, **kwargs):
    """
    str:initiator   Function or Part which fired the notification
    str:message     Main Body of Message

    str:title       Title of Message
    str:image       URL of Image
    str:url         URL contained with Message
    str:url_title   Title for the URL contained
    int:priority    Priority of Message
                    retry & expire is required with priority 2
                    Range       -2 ~ 2
                    Default     0
    int:retry       Seconds between retries
                    Range       30 ~ 10800
    int:expire      Seconds before retries stop
                    Range       30 ~ 10800
    """
    if "image" in kwargs and kwargs["image"]:
        img_url = kwargs["image"]
        kwargs["image"] = requests.get(img_url, stream=True).content
    pusher = pushover_complete.PushoverAPI(current_app.config["PUSHOVER_TOKEN"])
    return pusher.send_message(user.pushover, *args, **kwargs)
