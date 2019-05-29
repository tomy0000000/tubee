"""Helper Functions for Tubee"""
import codecs
import json
import os
from functools import wraps

import requests
import pushover_complete
import google.oauth2.credentials
import googleapiclient.discovery
from flask import abort, current_app, url_for
from flask_login import current_user
from google_auth_oauthlib.flow import Flow
from .. import db

def admin_required(func):
    """A decorator making view function for admin only"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.admin:
            abort(403)
        return func(*args, **kwargs)
    return decorated_function

def generate_random_id():
    """Generate a 16-chars long id"""
    return codecs.encode(os.urandom(16), "hex").decode()

def send_notification(initiator, user, *args, **kwargs):
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
    from ..models import Notification
    backup_kwargs = kwargs.copy()
    if "image" in kwargs and kwargs["image"]:
        img_url = kwargs["image"]
        kwargs["image"] = requests.get(img_url, stream=True).content
    pusher = pushover_complete.PushoverAPI(current_app.config["PUSHOVER_TOKEN"])
    response = pusher.send_message(user.pushover_key, *args, **kwargs)
    backup_kwargs["message"] = args[0]
    new = Notification(initiator, args[0][:2000], backup_kwargs, response)
    db.session.add(new)
    db.session.commit()
    return response

def new_send_notification(user, *args, **kwargs):
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
    return pusher.send_message(user.pushover_key, *args, **kwargs)

def auto_renew(channel):
    """Trigger channel"""
    response = channel.renew()
    current_app.logger.info("----------------Auto Renewed Start----------------")
    current_app.logger.info("{}<{}>".format(channel.channel_name, channel.channel_id))
    current_app.logger.info(response)
    current_app.logger.info("--------------Auto Renewed Complete--------------")
    return response
