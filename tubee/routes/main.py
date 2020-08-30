"""The Main Routes"""
from html import unescape
from urllib.parse import urljoin

import pyrfc3339
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from ..forms import ActionForm
from ..helper import youtube_required
from ..helper.youtube import build_youtube_api
from ..models import Callback, Channel, Subscription

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
@login_required
def dashboard():
    """Showing All Subscribed Channels"""
    subscriptions = (
        current_user.subscriptions.join(Subscription.channel)
        .order_by(Channel.name.asc())
        .all()
    )
    return render_template("dashboard.html", subscriptions=subscriptions)


@main_blueprint.route("/channel/<channel_id>")
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
        video["snippet"]["title"] = unescape(video["snippet"]["title"])
        video["snippet"]["publishedAt"] = pyrfc3339.parse(
            video["snippet"]["publishedAt"]
        )
        base_thumbnails_url = video["snippet"]["thumbnails"]["high"]["url"]
        video["snippet"]["thumbnails"]["standard"] = {
            "url": urljoin(base_thumbnails_url, "sddefault.jpg"),
            "width": 640,
            "height": 480,
        }
        video["snippet"]["thumbnails"]["maxres"] = {
            "url": urljoin(base_thumbnails_url, "maxresdefault.jpg"),
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
        "channel.html", channel=channel_item, actions=actions, form=form, videos=videos
    )


@main_blueprint.route("/youtube/subscription")
@login_required
@youtube_required
def youtube_subscription():
    return render_template("youtube_subscription.html")
