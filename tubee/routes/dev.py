"""Routes for Developing/Testing"""
import pprint
from os.path import basename

from dropbox.exceptions import ApiError
from dropbox.files import WriteMode
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from ..helper import admin_required, youtube_dl

dev_blueprint = Blueprint("dev", __name__)


@dev_blueprint.route("/test_schedule_job")
@login_required
@admin_required
def test_schedule_job():
    return render_template("empty.html")


@dev_blueprint.route("/request")
@login_required
@admin_required
def request_dict():
    target_dict = request.__dict__
    pprint_en = isinstance(target_dict, dict)
    if pprint_en:
        target_dict = pprint.pformat(target_dict)
    return render_template("empty.html", info=target_dict, pprint=pprint_en)


@dev_blueprint.route("/user")
@login_required
@admin_required
def user_dict():
    # target_dict = current_user.__dict__
    target_dict = {
        "is_authenticated": current_user.is_authenticated,
        "is_active": current_user.is_active,
        "is_anonymous": current_user.is_anonymous,
        "get_id()": current_user.get_id(),
    }
    pprint_en = isinstance(target_dict, dict)
    if pprint_en:
        target_dict = pprint.pformat(target_dict)
    return render_template("empty.html", info=target_dict, pprint=pprint_en)


@dev_blueprint.route("/empty")
def empty():
    return render_template("empty.html")


@dev_blueprint.route("/handler/<status_code>")
@login_required
@admin_required
def handler(status_code):
    abort(int(status_code))


@dev_blueprint.route("/test-dropbox")
@login_required
@admin_required
def test_dropbox():
    file_path = "instance/my-file.txt"
    filename = basename(file_path)
    with open(file_path, "rb") as file:
        try:
            response = current_user.dropbox.files_upload(
                file.read(), "/{}".format(filename), mode=WriteMode("overwrite")
            )
        except ApiError as error:
            flash(str(error), "danger")
        else:
            flash(str(response), "success")
    return redirect(url_for("main.dashboard"))


@dev_blueprint.route("/test-download-to-dropbox/<video_id>")
@login_required
@admin_required
def test_download_to_dropbox(video_id):
    metadata = youtube_dl.fetch_video_metadata(video_id)
    current_app.logger.info(metadata)
    response = current_user.dropbox.files_save_url(
        "/{}".format("{}.mp4".format(metadata["title"])), metadata["url"]
    )
    flash(str(response), "success")
    return redirect(url_for("main.dashboard"))
