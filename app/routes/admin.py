"""Routes for Admin Access"""
from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from .. import scheduler
from ..helper import admin_required
from ..models import Callback, Notification
admin_blueprint = Blueprint("admin", __name__)

@admin_blueprint.route("/notification/dashboard")
@login_required
@admin_required
def notification_dashboard():
    """Show Recent Pushed Notification"""
    # TODO
    notifications = Notification.query.order_by(Notification.sent_datetime.desc()).all()
    return render_template("pushover_dashboard.html", notifications=notifications)

@admin_blueprint.route("/notification/push", methods=["GET", "POST"])
@login_required
@admin_required
def notification_push():
    """Send Test Notification to User"""
    # TODO
    alert = alert_type = ""
    if request.method == "POST":
        form_datas = request.form
        alert = current_user.send_notification("Test", form_datas["message"], title=form_datas["title"])
        alert_type = "success"
    return render_template("pushover_push.html",
                           alert=alert,
                           alert_type=alert_type)

@admin_blueprint.route("/scheduler/dashboard")
@login_required
@admin_required
def scheduler_dashboard():
    """Show Scheduled Jobs"""
    jobs = scheduler.get_jobs().copy()
    return render_template("scheduler_dashboard.html", jobs=jobs)

@admin_blueprint.route("/hub/dashboard")
@login_required
@admin_required
def hub_dashboard():
    """List All Callbacks"""
    # TODO
    callbacks = Callback.query.order_by(Callback.received_datetime.desc()).all()
    return render_template("hub_dashboard.html", callbacks=callbacks)
