"""The Main Routes"""
from datetime import datetime, timedelta

import bs4
from flask import Blueprint, current_app, jsonify, render_template, request
from flask_login import current_user, login_required

from .. import db
from ..forms import ActionForm, TagForm
from ..helper import youtube_required
from ..helper.youtube import fetch_video_metadata
from ..models import Callback, Channel, SubscriptionTag, Tag, Video

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/", defaults={"tag": False})
@main_blueprint.route("/untagged", defaults={"tag": None})
@main_blueprint.route("/tag/<tag>")
@login_required
def dashboard(tag):
    """Showing Subscribed Channels with specified tag"""
    subscriptions = current_user.subscriptions.outerjoin(Channel).order_by(
        Channel.name.asc()
    )
    actions = None
    if tag is not False:
        subscriptions = (
            subscriptions.outerjoin(SubscriptionTag)
            .outerjoin(Tag)
            .filter(Tag.name == tag)
        )
        actions = current_user.actions.join(Tag).filter(Tag.name == tag)
    return render_template(
        "subscription.html",
        actions=actions,
        subscriptions=subscriptions.all(),
        tag=tag,
        action_form=ActionForm(),
    )


@main_blueprint.route("/channel/<channel_id>")
def channel(channel_id):
    subscription = current_user.subscriptions.filter_by(
        channel_id=channel_id
    ).first_or_404()
    videos = subscription.channel.videos.order_by(
        Video.uploaded_timestamp.desc()
    ).limit(20)
    return render_template(
        "channel.html",
        channel=subscription.channel,
        actions=subscription.actions,
        tags=subscription.tags,
        action_form=ActionForm(),
        tag_form=TagForm(),
        videos=videos,
    )


# TODO: REBUILD THIS
@main_blueprint.route("/channel/<channel_id>/callback", methods=["GET", "POST"])
def channel_callback(channel_id):
    """
    GET: Receive Hub Challenges to sustain subscription
    POST: New Update from Hub
    """
    channel_item = Channel.query.get_or_404(channel_id)
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
            current_app.logger.info(f"Video ID not Found for {callback_item}")
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
            video_file_url = fetch_video_metadata(video_id)["url"]
        except Exception:
            video_file_url = None

        # List users and execute actions
        for sub in channel_item.subscriptions:
            for action in sub.actions:
                try:
                    results = action.execute(
                        video_id=video_id,
                        video_title=video_item.name,
                        video_description=video_item.details["description"],
                        video_thumbnails=video_item.details["thumbnails"]["medium"][
                            "url"
                        ],
                        video_file_url=video_file_url,
                        channel_name=channel_item.name,
                    )
                except Exception as error:
                    results = {
                        "error": error.__class__.__name__,
                        "description": str(error),
                    }
                    current_app.logger.exception(f"{channel_id}-{action.id}: {error}")
                else:
                    current_app.logger.info(f"{channel_id}-{action.id}")
                response[action.id] = results
        return jsonify(response)


@main_blueprint.route("/youtube/subscription")
@login_required
@youtube_required
def youtube_subscription():
    return render_template("youtube_subscription.html")


@main_blueprint.route("/latest")
@login_required
def latest():
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    latest_video = Video.query.filter(Video.uploaded_timestamp > one_day_ago)
    user_subscribed_channels = [
        subscription.channel for subscription in current_user.subscriptions
    ]
    filtered_video = [
        video for video in latest_video if video.channel in user_subscribed_channels
    ]
    return render_template("latest.html", videos=filtered_video)
