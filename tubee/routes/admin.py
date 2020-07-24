"""Routes for Admin Access"""
import logging
import os
import platform
import sys

import flask
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

from ..helper import admin_required
from ..models import Callback, Notification, Service

admin_blueprint = Blueprint("admin", __name__)


@admin_blueprint.route("/dashboard")
@login_required
@admin_required
def admin_dashboard():
    links = {}
    for rule in current_app.url_map.iter_rules():
        query = {arg: f"[{arg}]" for arg in rule.arguments}
        url = url_for(rule.endpoint, **query)
        try:
            blueprint, endpoint = rule.endpoint.split(".")
            if blueprint in links:
                links[blueprint].append((url, rule.endpoint))
            else:
                links[blueprint] = [(url, rule.endpoint)]
        except ValueError:
            continue
    for blueprint, rules in links.items():
        rules.sort(key=lambda x: x[1])
    infos = {
        "os_version": platform.platform(),
        "python_version": sys.version,
        "flask_version": flask.__version__,
        "werkzeug_version": werkzeug.__version__,
        "app_config": current_app.config,
        "os_env": os.environ,
    }
    callbacks = Callback.query.order_by(Callback.timestamp.desc()).all()
    notifications = Notification.query.order_by(
        Notification.sent_timestamp.desc()
    ).paginate()
    return render_template(
        "admin_dashboard.html",
        infos=infos,
        callbacks=callbacks,
        notifications=notifications,
        links=links,
    )


@admin_blueprint.route("/raise-exception")
@login_required
@admin_required
def raise_exception():
    raise Exception


@admin_blueprint.route("/test-logging")
@login_required
@admin_required
def test_logging():
    logging.debug("debug Log")
    logging.info("info Log")
    logging.warning("warning Log")
    logging.error("error Log")
    logging.critical("critical Log")
    flash("Logged Success", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin_blueprint.route("/notification/push", methods=["POST"])
@login_required
@admin_required
def notification_push():
    """Send Test Notification to User"""
    if request.method == "POST":
        response = current_user.send_notification(
            "Test",
            Service(request.form.get("service", "Pushover")),
            message=request.form["message"],
        )
        flash(response, "success")
        return redirect(url_for("admin.admin_dashboard"))
