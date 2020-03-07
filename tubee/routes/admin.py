"""Routes for Admin Access"""
import os
from flask import Blueprint, current_app, flash, render_template, request
from flask_login import current_user, login_required
from ..helper import admin_required
from ..models import Callback, Notification, Service
admin_blueprint = Blueprint("admin", __name__)


@admin_blueprint.route("/server")
@login_required
@admin_required
def server():
    os_environment_variables = os.environ
    flask_config = current_app.config
    # return render_template("")


@admin_blueprint.route("/notification/dashboard")
@login_required
@admin_required
def notification_dashboard():
    """Show Recent Pushed Notification"""
    # TODO
    notifications = Notification.query.order_by(
        Notification.sent_datetime.desc()).paginate()
    return render_template("notification_dashboard.html",
                           notifications=notifications)


@admin_blueprint.route("/notification/push", methods=["GET", "POST"])
@login_required
@admin_required
def notification_push():
    """Send Test Notification to User"""
    if request.method == "POST":
        response = current_user.send_notification(
            "Test",
            Service(request.form.get("service", "Pushover")),
            message=request.form["message"])
        flash(response, "success")
    return render_template("test_notification.html")


@admin_blueprint.route("/hub/dashboard")
@login_required
@admin_required
def hub_dashboard():
    """List All Callbacks"""
    # TODO
    callbacks = Callback.query.order_by(
        Callback.received_datetime.desc()).all()
    return render_template("hub_dashboard.html", callbacks=callbacks)
