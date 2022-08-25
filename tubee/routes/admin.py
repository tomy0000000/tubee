from flask import Blueprint, current_app, render_template
from flask_login import login_required

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
