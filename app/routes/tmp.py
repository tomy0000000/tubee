"""Beta views"""
import random
from datetime import datetime, timedelta
from flask import redirect, render_template, session, url_for
from flask_login import current_user, login_required
from .. import scheduler, oauth
from ..helper import admin_required, youtube_dl
from ..models import Channel
from .dev import dev_blueprint

@dev_blueprint.route("/missle_testing")
def register_auto_renew_test():
    response = None
    channel = Channel.query.first()
    infos = channel.renew_hub()
    delta = infos["expiration"] - datetime.now()
    random_num = random.randint(0, delta)
    renew_datetime = datetime.now() + timedelta(seconds=random_num)
    scheduler.add_job("renew_channel_{}".format(channel.channel_id), test_func, run_date=renew_datetime)
    return render_template("empty.html", info=response)

@dev_blueprint.route("/missle_launched")
def register_auto_renew_official():
    response = None
    return render_template("empty.html", info=response)

def test_func_auto_reschedule():
    print("hello")
    job = scheduler.get_job("test_resch")
    random_num = random.randint(0, 30)
    print("next run at {} seconds later".format(random_num))
    target_datetime = datetime.now() + timedelta(seconds=random_num)
    # job.reschedule(run_date=target_datetime)
    response = scheduler.add_job("test_resch", test_func_auto_reschedule, run_date=target_datetime)

@dev_blueprint.route("/regist_job_resch")
@login_required
@admin_required
def regist_job_resch():
    target_datetime = datetime.now() + timedelta(seconds=10)
    response = scheduler.add_job("test_resch", test_func_auto_reschedule, run_date=target_datetime)
    return render_template("empty.html", info=response)

@dev_blueprint.route("/remove_job_resch")
@login_required
@admin_required
def remove_job_resch():
    response = scheduler.remove_job("test_resch")
    return render_template("empty.html", info=response)

def test_func():
    print("123")

@dev_blueprint.route("/regist_job")
@login_required
@admin_required
def regist_job():
    response = scheduler.add_job("test", test_func, trigger="interval", seconds=2)
    return render_template("empty.html", info=response)

@dev_blueprint.route("/remove_job")
@login_required
@admin_required
def remove_job():
    response = scheduler.remove_job("test")
    return render_template("empty.html", info=response)

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
