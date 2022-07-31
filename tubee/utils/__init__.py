"""Helper Functions

Some Misc Functions used in this app
"""
import secrets
import string
from functools import wraps
from urllib.parse import unquote, urljoin, urlparse

from dateutil import parser
from flask import abort, current_app, jsonify, request, url_for
from flask_login import current_user
from flask_migrate import upgrade
from werkzeug.exceptions import HTTPException

from ..exceptions import TubeeError


def setup_app():
    # Migrate database to latest revision
    upgrade()
    current_app.logger.info("Database migrated")

    from ..models.user import User

    # Create an admin user if none exists
    if not User.query.filter_by(admin=True).first():
        # Create a random password
        alphabet = string.ascii_letters + string.digits
        password = "".join(secrets.choice(alphabet) for i in range(20))

        User(username="admin", password=password, admin=True)
        current_app.db.session.commit()
        current_app.logger.info("Admin created automatically:")
        current_app.logger.info("Username: admin")
        current_app.logger.info(f"Password: {password}")

    # Reschedule all tasks
    from ..models import Channel
    from ..tasks import remove_all_tasks, schedule_channel_renewal

    remove_all_tasks()
    current_app.logger.info("All tasks removed")
    schedule_channel_renewal(Channel.query.all())
    current_app.logger.info("Channel renewal scheduled")

    # TODO: Update channels metadata


def try_parse_datetime(string):
    try:
        return parser.parse(string).replace(tzinfo=None)
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


def api_error_handler(error):
    """Handle API Errors

    Arguments:
        error {Exception} -- The error to be handled

    Returns:
        Response -- Wrapped JSON response
    """
    if isinstance(error, HTTPException):  # raised with flask.abort(code, description)
        description = error.description
        status_code = error.code
    elif isinstance(error, TubeeError):
        description = error.description
        status_code = 400
    else:
        description = "Internal Server Error"
        status_code = 500
    return (
        jsonify(ok=False, error=error.__class__.__name__, description=str(description)),
        status_code,
    )
