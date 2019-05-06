"""Routes for Admin Access"""
from flask import Blueprint, render_template
from flask_login import login_required
from .. import scheduler
from ..models import Notification
admin = Blueprint("admin", __name__)

@admin.route("/dashboard/notification")
@login_required
def dashboard_notification():
    """Show Recent Pushed Notification"""
    # TODO
    notifications = Notification.query.order_by(Notification.sent_datetime.desc()).all()
    return render_template("pushover_history.html", notifications=notifications)

@admin.route("/dashboard/scheduler_jobs")
@login_required
def dashboard_scheduler_jobs():
    """Show Scheduled Jobs"""
    # TODO
    jobs = scheduler.get_jobs().copy()
    for ind, val in enumerate(jobs):
        jobs[ind] = str(val)
    return render_template("empty.html", info=jobs)
