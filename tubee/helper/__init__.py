"""Helper Functions

Some Misc Functions used in this app
"""
from functools import wraps
from urllib.parse import urljoin, urlparse

from dateutil import parser
from flask import abort, request
from flask_login import current_user
from flask_migrate import upgrade


def setup_app():
    # Migrate database to latest revision
    upgrade()

    # Reschedule all tasks
    from ..models import Channel
    from ..tasks import remove_all_tasks, schedule_channel_renewal

    channels = Channel.query.all()
    remove_all_tasks()
    schedule_channel_renewal(channels)


def try_parse_datetime(string):
    try:
        return parser.parse(string).replace(tzinfo=None)
    except (ValueError, TypeError):
        return None


def admin_required(*args, **kwargs):
    if not current_user.admin:
        abort(403)


def admin_required_decorator(func):
    """Restrict view function to admin-only

    Arguments:
        func {view function} -- The view function to be restricting

    Returns:
        view function -- The restricted function
    """

    @wraps(func)
    def decorated_view_function(*args, **kwargs):
        admin_required()
        return func(*args, **kwargs)

    return decorated_view_function


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
        dict -- Response from notification service
    """
    from ..models.user import User

    admins = User.query.filter_by(admin=True).all()
    response = {}
    for admin in admins:
        response[admin.username] = admin.send_notification(initiator, service, **kwargs)
    return response
