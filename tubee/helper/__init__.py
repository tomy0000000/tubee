"""Helper Functions

Some Misc Functions used in this app
"""
import logging
from datetime import datetime
from functools import wraps
from urllib.parse import urlencode, urljoin, urlparse

from dateutil import parser
from flask import abort, current_app, request, url_for
from flask_login import current_user

# from google.cloud import tasks_v2


def try_parse_datetime(string):
    try:
        return parser.parse(string).replace(tzinfo=None)
    except (ValueError, TypeError):
        return None


def admin_required(func):
    """Restrict view function to admin-only

    Arguments:
        func {view function} -- The view function to be restricting

    Returns:
        view function -- The restricted function
    """

    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.admin:
            abort(403)
        return func(*args, **kwargs)

    return decorated_function


def app_engine_required(func):
    """Restrict view function to app-engine-triggered-only

    Arguments:
        func {view function} -- The view function to be restricting

    Returns:
        view function -- The restricted function
    """

    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not request.headers.get("X-Appengine-Cron"):
            logging.info("Forbidden Triggered at {}".format(datetime.now()))
            abort(401)
        return func(*args, **kwargs)

    return decorated_function


def pushover_required(func):
    """Restrict view function to users who have configured Pushover account

    Arguments:
        func {view function} -- The view function to be restricting

    Returns:
        view function -- The restricted function
    """

    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.pushover:
            abort(403)
        return func(*args, **kwargs)

    return decorated_function


def youtube_required(func):
    """Restrict view function to users who have configured YouTube account

    Arguments:
        func {view function} -- The view function to be restricting

    Returns:
        view function -- The restricted function
    """

    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.youtube:
            abort(403)
        return func(*args, **kwargs)

    return decorated_function


def is_safe_url(target):
    """Helper used to check endpoint before redirecting user

    Arguments:
        target {url} -- a url with complete scheme and domain to be examine

    Returns:
        bool -- target is a safe url or not
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def notify_admin(initiator, service, **kwargs):
    """Send Notification to all Admin

    A Temporary function used to notify admin

    Arguments:
        initiator {str} -- Action or reason that trigger this notification
        service {str or notification.Service} -- Service used to send notification
        **kwargs {dict} -- optional arguments passed to notification

    Returns:
        dict -- Reponse from notification service
    """
    from ..models.user import User

    admins = User.query.filter_by(admin=True).all()
    response = {}
    for admin in admins:
        if admin.pushover:
            response[admin.username] = admin.send_notification(
                initiator, service, **kwargs
            )
    return response


def build_callback_url(channel_id):
    callback_url = url_for("channel.callback", channel_id=channel_id, _external=True)
    # if current_app.config["HUB_RECEIVE_DOMAIN"]:
    #     callback_url = callback_url.replace(
    #         request.host, current_app.config["HUB_RECEIVE_DOMAIN"]
    #     )
    return callback_url


def build_topic_url(channel_id):
    param_query = urlencode({"channel_id": channel_id})
    return current_app.config["HUB_YOUTUBE_TOPIC"] + param_query


# def build_cloud_task_service():
#     client = tasks_v2.CloudTasksClient()
#     parent = client.queue_path(
#         current_app.config["GOOGLE_CLOUD_PROJECT_ID"],
#         current_app.config["GOOGLE_CLOUD_LOCATION"],
#         current_app.config["GOOGLE_CLOUD_TASK_QUEUE"],
#     )
#     return client, parent
