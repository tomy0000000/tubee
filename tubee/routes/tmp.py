"""Beta views"""
from flask import redirect, render_template, session, url_for
from flask_login import current_user, login_required
from .. import oauth
from ..helper import admin_required, youtube_dl
from .dev import dev_blueprint

@dev_blueprint.route("/post-line-notify")
@login_required
@admin_required
def send_line():
    response = oauth.LineNotify.post("api/notify", data={"message": "Test message"})
    print(response)
    return render_template("empty.html", info=response.text)

@dev_blueprint.route("/test-dropbox")
@login_required
@admin_required
def test_dropbox():
    response = current_user.save_file_to_dropbox("instance/my-file.txt")
    if response[0]:
        session["alert_type"] = "success"
    else:
        session["alert_type"] = "danger"
    session["alert"] = str(response[1])
    return redirect(url_for("main.dashboard"))

@dev_blueprint.route("/test-download-to-dropbox/<video_id>")
@login_required
@admin_required
def test_download_to_dropbox(video_id):
    metadata = youtube_dl.fetch_video_metadata(video_id)
    response = current_user.save_url_to_dropbox(metadata["url"], "{}.mp4".format(metadata["title"]))
    if response[0]:
        session["alert_type"] = "success"
    else:
        session["alert_type"] = "danger"
    session["alert"] = str(response[1])
    return redirect(url_for("main.dashboard"))
