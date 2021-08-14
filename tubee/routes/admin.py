"""Routes for Admin Access"""
import os
import platform
import sys
from urllib.parse import unquote

import flask
import gunicorn
import werkzeug
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from ..models import Callback, Channel, Notification
from ..utils import admin_required

admin_blueprint = Blueprint("admin", __name__)
admin_blueprint.before_request(admin_required)


@admin_blueprint.route("/dashboard")
@login_required
def dashboard():
    # Sitemap
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
    # System Runtime
    infos = {
        "os_version": platform.platform(),
        "python_version": sys.version,
        "werkzeug_version": werkzeug.__version__,
        "flask_version": flask.__version__,
        "gunicorn_version": gunicorn.SERVER_SOFTWARE,
        "tubee_version": current_app.version,
        "app_config": current_app.config,
        "os_env": os.environ,
    }
    # Miscs
    channels = Channel.query.order_by(Channel.name.asc()).all()
    callbacks = Callback.query.order_by(Callback.timestamp.desc()).limit(50)
    notifications = Notification.query.order_by(
        Notification.sent_timestamp.desc()
    ).limit(50)
    return render_template(
        "admin.html",
        callbacks=callbacks,
        channels=channels,
        infos=infos,
        links=links,
        notifications=notifications,
    )


@admin_blueprint.route("/raise-exception")
@login_required
def raise_exception():
    raise Exception


@admin_blueprint.route("/test-logging")
@login_required
def test_logging():
    current_app.logger.debug("debug Log")
    current_app.logger.info("info Log")
    current_app.logger.warning("warning Log")
    current_app.logger.error("error Log")
    current_app.logger.critical("critical Log")
    flash("Logged Success", "success")
    return redirect(url_for("admin.dashboard"))


@admin_blueprint.route("/notification/push", methods=["POST"])
@login_required
def notification_push():
    """Send Test Notification to User"""
    if request.method == "POST":
        response = current_user.send_notification(
            "Test",
            "Pushover",
            message=request.form["message"],
        )
        flash(response, "success")
        return redirect(url_for("admin.dashboard"))
