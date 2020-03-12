"""Beta views"""
from os.path import basename
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError
from flask import current_app, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from ..helper import admin_required, youtube_dl
from .dev import dev_blueprint


@dev_blueprint.route("/post-line-notify")
@login_required
@admin_required
def send_line():
    response = current_user.line_notify.post("api/notify",
                                             data={"message": "Test message"})
    return render_template("empty.html", info=response.text)


@dev_blueprint.route("/test-dropbox")
@login_required
@admin_required
def test_dropbox():
    file_path = "instance/my-file.txt"
    filename = basename(file_path)
    with open(file_path, "rb") as file:
        try:
            response = current_user.dropbox.files_upload(
                file.read(),
                "/{}".format(filename),
                mode=WriteMode("overwrite"))
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
        "/{}".format("{}.mp4".format(metadata["title"])), metadata["url"])
    flash(str(response), "success")
    return redirect(url_for("main.dashboard"))
