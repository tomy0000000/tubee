"""Helper Functions

Some Misc Functions used in this app
"""
import logging
import secrets
import string
from datetime import datetime
from functools import wraps
from typing import Union
from urllib.parse import unquote, urljoin, urlparse

from dateutil import parser
from flask import current_app  # type: ignore
from flask import abort, request, url_for
from flask_login import current_user  # type: ignore
from flask_migrate import upgrade
from loguru import logger

from .. import Tubee
from ..models import User

current_app: Tubee
current_user: User


class PropagateToGunicorn(logging.Handler):
    def emit(self, record):
        logging.getLogger("gunicorn.error").handle(record)


def setup_app():
    # Migrate database to latest revision
    upgrade()
    logger.info("Database migrated")

    from ..models.user import User

    # Create an admin user if none exists
    if not User.query.filter_by(admin=True).first():
        # Create a random password
        alphabet = string.ascii_letters + string.digits
        password = "".join(secrets.choice(alphabet) for i in range(20))

        User(username="admin", password=password, admin=True)
        current_app.db.session.commit()
        logger.info("Admin created automatically:")
        logger.info("Username: admin")
        logger.info(f"Password: {password}")

    # Reschedule all tasks
    from ..models import Channel
    from ..tasks import remove_all_tasks, schedule_channel_renewal

    remove_all_tasks()
    logger.info("All tasks removed")
    schedule_channel_renewal(Channel.query.all())
    logger.info("Channel renewal scheduled")

    # TODO: Update channels metadata


def try_parse_datetime(string: str, fuzzy: bool = False) -> Union[datetime, None]:
    try:
        return parser.parse(string, fuzzy=fuzzy).replace(tzinfo=None)
    except (ValueError, TypeError):
        return None


def build_sitemap():
    """Build Sitemap

    Builds a sitemap of all endpoints in the app

    Returns:
        str -- Sitemap
    """

    links = {}
    for rule in current_app.url_map.iter_rules():
        query = {arg: f"<{arg}>" for arg in rule.arguments}
        url = url_for(rule.endpoint, **query)
        try:
            blueprint, endpoint = rule.endpoint.split(".")
            url = unquote(url)
            if blueprint in links:
                links[blueprint].append((url, rule.endpoint))
            else:
                links[blueprint] = [(url, rule.endpoint)]
        except ValueError:
            continue
    for blueprint, rules in links.items():
        rules.sort(key=lambda x: x[1])
    links["static"] = [("/static/<filename>", "static")]
    return links


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


def get_line_notify_fetch_token() -> dict:
    """Get Line Notify Fetch Token

    Returns:
        dict -- Line Notify Fetch Token
    """
    return dict(access_token=current_user._line_notify_credentials, token_type="bearer")
