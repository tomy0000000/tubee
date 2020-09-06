from datetime import datetime, timedelta
from uuid import uuid4

from flask import Blueprint, jsonify, request, url_for
from flask_login import current_user, login_required

from ..helper import admin_required_decorator, build_callback_url, build_topic_url
from ..helper.youtube import build_youtube_api
from ..models import Channel
from ..tasks import renew_channels

api_channel_blueprint = Blueprint("api_channel", __name__)


@api_channel_blueprint.route("/<query>")
@login_required
def search(query):
    response = (
        build_youtube_api()
        .search()
        .list(part="snippet", maxResults=30, q=query, type="channel")
        .execute()
    )
    results = [
        {
            "title": item["snippet"]["title"],
            "id": item["snippet"]["channelId"],
            "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
        }
        for item in response["items"]
    ]
    return jsonify(results)


@api_channel_blueprint.route("/renew-all")
@login_required
def renew_all():
    """Renew Subscription Info, Both Hub and Info"""
    next_countdown = int(request.args.to_dict().get("next_countdown", -1))
    immediate = bool(next_countdown <= 0)
    compact_args = []
    response = {}
    for channel in Channel.query.all():
        task_args = (
            channel.id,
            build_callback_url(channel.id),
            build_topic_url(channel.id),
        )
        if immediate:
            compact_args.append(task_args)
        else:
            expiration = channel.expiration
            if expiration is None:
                eta = datetime.now() + timedelta(days=4)
            elif expiration > datetime.now() + timedelta(days=1):
                eta = expiration - timedelta(days=1)
            else:
                eta = datetime.now()
            task = renew_channels.apply_async(
                args=[[task_args], next_countdown],
                eta=eta,
                task_id=f"renew_{channel.id}_{str(uuid4())[:8]}",
            )
            response[channel.id] = task.id
    if immediate:
        task = renew_channels.apply_async(args=[compact_args])
        response = {
            "id": task.id,
            "status": url_for("api_task.status", task_id=task.id),
        }
    return jsonify(response)


@api_channel_blueprint.route("/<channel_id>/status")
@login_required
def status(channel_id):
    """From Hub fetch Status"""
    channel = Channel.query.filter_by(id=channel_id).first_or_404()
    response = channel.update_hub_infos()
    return jsonify(response)


@api_channel_blueprint.route("/<channel_id>/subscribe")
@login_required
def subscribe(channel_id):
    """Subscribe to a Channel"""
    return jsonify(current_user.subscribe_to(channel_id))


@api_channel_blueprint.route("/<channel_id>/unsubscribe")
@login_required
def unsubscribe(channel_id):
    """Unsubscribe to a Channel"""
    return jsonify(current_user.unbsubscribe(channel_id))


@api_channel_blueprint.route("/<channel_id>/renew")
@login_required
def renew(channel_id):
    """Renew Subscription Info, Both Hub and Info"""
    channel = Channel.query.filter_by(id=channel_id).first_or_404()
    response = channel.renew(stringify=True)
    return jsonify(response)


@api_channel_blueprint.route("/<channel_id>/fetch-videos")
@login_required
@admin_required_decorator
def fetch_videos(channel_id):
    # TODO: deprecate this
    channel_item = Channel.query.filter_by(id=channel_id).first_or_404()
    response = channel_item.fetch_videos()
    return jsonify(response)
