"""Routes for Developing/Testing"""
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    url_for,
)
from flask_login import current_user, login_required

from ..helper import youtube_dl

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
    metadata = youtube_dl.fetch_video_metadata(video_id)
    current_app.logger.info(metadata)
    response = current_user.dropbox.files_save_url(
        "/{}".format("{}.mp4".format(metadata["title"])), metadata["url"]
    )
    flash(str(response), "success")
    return redirect(url_for("main.dashboard"))
