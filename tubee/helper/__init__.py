"""Helper Functions

Some Misc Functions used in this app
"""
from datetime import datetime
from functools import wraps
from urllib.parse import urlparse, urljoin
from flask import abort, current_app, request
from flask_login import current_user
from ..models.user import User


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
            current_app.logger.info("Forbidden Triggered at {}".format(
                datetime.now()))
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
    return test_url.scheme in ("http",
                               "https") and ref_url.netloc == test_url.netloc


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
    admins = User.query.filter_by(admin=True).all()
    response = {}
    for admin in admins:
        if admin.pushover:
            response[admin.username] = admin.send_notification(
                initiator, service, **kwargs)
    return response
