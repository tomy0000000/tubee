"""Channel Related Routes"""
import bs4
import logging
import pyrfc3339
from datetime import datetime, timedelta
from flask import (
    Blueprint,
    flash,
    jsonify,
    render_template,
    redirect,
    request,
    url_for,
)
from flask_login import current_user, login_required
from .. import db
from ..forms import ActionForm
from ..helper import notify_admin, youtube_dl
from ..helper.youtube import build_youtube_api
from ..models import Callback, Channel, Subscription, Video

channel_blueprint = Blueprint("channel", __name__)


@channel_blueprint.route("/<channel_id>")
def channel(channel_id):
    channel_item = Channel.query.filter_by(id=channel_id).first_or_404()
    videos = (
        build_youtube_api()
        .search()
        .list(
            part="snippet",
            channelId=channel_id,
            maxResults=50,
            order="date",
            type="video",
        )
        .execute()["items"]
    )
    for video in videos:
        video["snippet"]["publishedAt"] = pyrfc3339.parse(
            video["snippet"]["publishedAt"]
        )
        base_thumbnails_url = "/".join(
            video["snippet"]["thumbnails"]["high"]["url"].split("/")[:-1]
        )
        video["snippet"]["thumbnails"]["standard"] = {
            "url": base_thumbnails_url + "/sddefault.jpg",
            "width": 640,
            "height": 480,
        }
        video["snippet"]["thumbnails"]["maxres"] = {
            "url": base_thumbnails_url + "/maxresdefault.jpg",
            "width": 1280,
            "height": 720,
        }
        callback_search = (
            Callback.query.filter_by(
                channel_id=channel_id,
                type="Hub Notification",
                video_id=video["id"]["videoId"],
            )
            .order_by(Callback.timestamp.asc())
            .all()
        )
        video["snippet"]["callback"] = {
            "datetime": callback_search[0].timestamp if bool(callback_search) else "",
            "count": len(callback_search),
        }
    actions = (
        current_user.subscriptions.filter_by(channel_id=channel_id)
        .first()
        .actions.all()
    )
    form = ActionForm()
    return render_template(
        "channel.html", channel=channel_item, videos=videos, actions=actions, form=form
    )


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


# TODO: REBUILD THIS DAMN MESSY ROUTE
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
            logging.info("Video ID not Found for {}".format(callback_item))
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

        # # Auto Renew if expiration is close
        # expiration = channel_item.expiration
        # if expiration and expiration - datetime.now() < timedelta(days=2):
        #     response["renew"] = channel_item.renew()
        #     logging.info("Channel renewed during callback")
        #     logging.info(response["renew"])
        #     notify_admin(
        #         "Deployment",
        #         "Pushover",
        #         message="{} <{}>".format(channel_item.name, channel_item.id),
        #         title="Channel renewed during callback",
        #     )

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
                logging.info("{}-{}: {}".format(sub.username, action.id, results))
                response[sub.username][action.id] = str(results)
        return jsonify(response)
