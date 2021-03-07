"""Routes for Developing/Testing"""
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import current_user, login_required

from ..helper.youtube import fetch_video_metadata

dev_blueprint = Blueprint("dev", __name__)


@dev_blueprint.before_request
def admin_required():
    if not current_user.admin:
        abort(403)


@dev_blueprint.route("/empty")
def empty():
    return render_template("empty.html")


@dev_blueprint.route("/test-download-to-dropbox/<video_id>")
@login_required
def test_download_to_dropbox(video_id):
    metadata = fetch_video_metadata(video_id)
    response = current_user.dropbox.files_save_url(
        f"/{metadata['title']}.mp4", metadata["url"]
    )
    flash(str(response), "success")
    return redirect(url_for("main.dashboard"))
