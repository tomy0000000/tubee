"""Beta views"""
import random
from datetime import datetime, timedelta, timezone
from flask import redirect, render_template, session, url_for, current_app
from flask_login import current_user, login_required
from .. import scheduler, oauth
from ..helper import admin_required, schedule_function, youtube_dl
from ..models import Channel
from .dev import dev_blueprint

@dev_blueprint.route("/<channel_id>/register_auto_renew")
def register_auto_renew(channel_id):
    channel = Channel.query.filter_by(channel_id=channel_id).first_or_404()

    # Setup runtime
    infos = channel.renew_hub()
    current_app.logger.info(infos["expiration"])
    delta = infos["expiration"] - datetime.now(timezone.utc)
    random_num = random.randint(0, int(delta.total_seconds()))
    renew_datetime = datetime.now() + timedelta(seconds=random_num)

    # Setup runtime (beta)
    # renew_datetime = datetime.now() + timedelta(seconds=10)

    response = scheduler.add_job(id="renew_channel_{}".format(channel.channel_name),
                                 func=schedule_function.renew_channel,
                                 args=[channel],
                                 run_date=renew_datetime)
    return render_template("empty.html", info=response)

@dev_blueprint.route("/<channel_id>/deregister_auto_renew")
@login_required
@admin_required
def deregister_auto_renew(channel_id):
    channel = Channel.query.filter_by(channel_id=channel_id).first_or_404()
    scheduler.remove_job("renew_channel_{}".format(channel.channel_name))
    return redirect(url_for("admin.scheduler_dashboard"))

@dev_blueprint.route("/register_test_job")
@login_required
@admin_required
def register_test_job():
    response = scheduler.add_job("test", schedule_function.test_func, trigger="interval", seconds=2)
    return render_template("empty.html", info=response)

@dev_blueprint.route("/remove_test_job")
@login_required
@admin_required
def remove_test_job():
    scheduler.remove_job("test")
    return redirect(url_for("admin.scheduler_dashboard"))




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
