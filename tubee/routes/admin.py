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

from ..models import Channel
from ..tasks import list_all_tasks
from ..utils import admin_required, build_sitemap

admin_blueprint = Blueprint("admin", __name__)
admin_blueprint.before_request(admin_required)


@admin_blueprint.get("/")
@login_required
def dashboard():
    links = build_sitemap()
    return render_template("admin/main.html", links=links, version=current_app.version)


@admin_blueprint.get("/channels")
def channels():
    channels = Channel.query.all()
    tasks = list_all_tasks()
    return render_template("admin/channels_page.html", channels=channels, tasks=tasks)


@admin_blueprint.get("/raise-exception")
@login_required
def raise_exception():
    raise Exception


@admin_blueprint.get("/test-logging")
@login_required
def test_logging():
    current_app.logger.debug("debug Log")
    current_app.logger.info("info Log")
    current_app.logger.warning("warning Log")
    current_app.logger.error("error Log")
    current_app.logger.critical("critical Log")
    flash("Logged Success", "success")
    return redirect(url_for("admin.dashboard"))


@admin_blueprint.post("/notification/push")
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
