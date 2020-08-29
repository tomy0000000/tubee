"""Channel Related Routes"""
import bs4
from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from .. import db
from ..helper import youtube_dl
from ..models import Callback, Channel, Subscription, Video

channel_blueprint = Blueprint("channel", __name__)


@channel_blueprint.route("/subscribe", methods=["GET", "POST"])
@login_required
def subscribe():
    """Page To Add Subscription"""
    if request.method == "GET":
        return render_template("subscribe.html")
    if request.method == "POST" and current_user.subscribe_to(
        request.form["channel_id"]
    ):
        flash("Subscribe Success", "success")
    else:
        flash("Oops! Subscribe Failed for some reason", "danger")
    return redirect(url_for("main.dashboard"))


# TODO: REBUILD THIS
@channel_blueprint.route("/<channel_id>/callback", methods=["GET", "POST"])
def callback(channel_id):
    """
    GET: Receive Hub Challenges to sustain subscription
    POST: New Update from Hub
    """
    channel_item = Channel.query.filter_by(id=channel_id).first_or_404()
    callback_item = Callback(channel_item)
    infos = {
        "method": request.method,
        "arguments": request.args,
        "user_agent": str(request.user_agent),
    }
    if request.method == "GET":
        response = request.args.to_dict().get("hub.challenge")
        if response:
            callback_item.type = "Hub Challenge"
            infos["details"] = response
            callback_item.infos = infos
        else:
            response = callback_item.type = "Unknown GET Request"
        db.session.commit()
        return response
    elif request.method == "POST":

        # Preprocessing
        infos["data"] = request.get_data(as_text=True)
        soup = bs4.BeautifulSoup(infos["data"], "xml")
        response = {}
        # TODO: Inspecting

        tag = soup.find("yt:videoId")
        if tag is None:
            current_app.logger.info("Video ID not Found for {}".format(callback_item))
            callback_item.infos = infos
            db.session.commit()
            return response
        video_id = tag.string

        # Update Database Records
        video_item = Video.query.get(video_id)
        new_video = not bool(video_item)
        if new_video:
            video_item = Video(video_id, channel_item)
        video_item.callbacks.append(callback_item)
        callback_item.video = video_item
        callback_item.type = "Hub Notification"
        callback_item.infos = infos
        db.session.commit()

        # Pass actions if not new video
        if not new_video:
            return jsonify(response)

        # Fetch Video Infos
        try:  # TODO
            video_file_url = youtube_dl.fetch_video_metadata(video_id)["url"]
        except Exception:
            video_file_url = None

        # List users and execute actions
        for sub in Subscription.query.filter_by(channel_id=channel_id).all():
            response[sub.username] = {}
            for action in sub.actions:
                try:
                    results = action.execute(
                        video_id=video_id,
                        video_title=video_item.name,
                        video_description=video_item.details["snippet"]["description"],
                        video_thumbnails=video_item.details["snippet"]["thumbnails"][
                            "medium"
                        ]["url"],
                        video_file_url=video_file_url,
                        channel_name=channel_item.name,
                    )
                except Exception as error:
                    results = error
                current_app.logger.info(
                    "{}-{}: {}".format(sub.username, action.id, results)
                )
                response[sub.username][action.id] = str(results)
        return jsonify(response)
