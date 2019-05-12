"""Routes for Admin Access"""
from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from .. import scheduler
from ..helper import admin_required
from ..models import Callback, Notification
admin = Blueprint("admin", __name__)

@admin.route("/notification/dashboard")
@login_required
@admin_required
def notification_dashboard():
    """Show Recent Pushed Notification"""
    # TODO
    notifications = Notification.query.order_by(Notification.sent_datetime.desc()).all()
    return render_template("pushover_history.html", notifications=notifications)

@admin.route("/notification/push", methods=["GET", "POST"])
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

@admin.route("/scheduler/dashboard")
@login_required
@admin_required
def scheduler_dashboard():
    """Show Scheduled Jobs"""
    # TODO
    jobs = scheduler.get_jobs().copy()
    for ind, val in enumerate(jobs):
        jobs[ind] = str(val)
    return render_template("empty.html", info=jobs)

@admin.route("/hub/dashboard")
@login_required
@admin_required
def hub_dashboard():
    """List All Callbacks"""
    # TODO
    callbacks = Callback.query.order_by(Callback.received_datetime.desc()).all()
    return render_template("hub_history.html", callbacks=callbacks)
