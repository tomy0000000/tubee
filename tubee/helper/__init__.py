"""Helper Functions"""
from datetime import datetime
from functools import wraps
from urllib.parse import urlparse, urljoin
from flask import abort, current_app, request
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


def app_engine_required(func):
    """Restrict view function to app-engine-triggered-only"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not request.headers.get("X-Appengine-Cron"):
            current_app.logger.info("Forbidden Triggered at {}".format(
                datetime.now()))
            abort(401)
        return func(*args, **kwargs)

    return decorated_function


def pushover_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.pushover:
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


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http",
                               "https") and ref_url.netloc == test_url.netloc


def notify_admin(initiator, service, **kwargs):
    """Send Notification to all Admin with pushover set"""
    admins = User.query.filter_by(admin=True).all()
    response = {}
    for admin in admins:
        if admin.pushover:
            response[admin.username] = admin.send_notification(
                initiator, service, **kwargs)
    return response
