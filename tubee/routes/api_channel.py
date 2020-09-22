from datetime import datetime, timedelta
from random import randrange
from uuid import uuid4

import requests
from flask import Blueprint, jsonify, request, url_for
from flask_login import current_user, login_required

from ..helper import admin_required_decorator
from ..models import Channel
from ..tasks import renew_channels

api_channel_blueprint = Blueprint("api_channel", __name__)


@api_channel_blueprint.route("/search")
@login_required
def search():
    query = request.args.get("query")

    URL = f"https://www.youtube.com/results?search_query={query}&sp=EgIQAg%253D%253D&pbj=1"
    HEADERS = {
        "x-youtube-client-name": "1",
        "x-youtube-client-version": "2.20200915.04.01",
    }
    PATH = [
        1,
        "response",
        "contents",
        "twoColumnSearchResultsRenderer",
        "primaryContents",
        "sectionListRenderer",
        "contents",
        0,
        "itemSectionRenderer",
        "contents",
    ]

    contents = requests.get(URL, headers=HEADERS).json()
    for key in PATH:
        contents = contents[key]
    results = [
        {
            "title": item["channelRenderer"]["title"]["simpleText"],
            "id": item["channelRenderer"]["channelId"],
            "thumbnail": item["channelRenderer"]["thumbnail"]["thumbnails"][-1]["url"],
        }
        for item in contents
    ]
    # response = (
    #     build_youtube_api()
    #     .search()
    #     .list(part="snippet", maxResults=30, q=query, type="channel")
    #     .execute()
    # )
    # results = response
    # results = [
    #     {
    #         "title": item["snippet"]["title"],
    #         "id": item["snippet"]["channelId"],
    #         "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
    #     }
    #     for item in response["items"]
    # ]
    return jsonify(results)


@api_channel_blueprint.route("/renew-all")
@login_required
def renew_all():
    """Renew Subscription Info, Both Hub and Info"""
    execution = int(request.args.to_dict().get("execution", 0))
    interval = 60 * 60 * 24 * 4
    if execution == 0:
        task = renew_channels.apply_async(
            args=[[channel.id for channel in Channel.query.all()]]
        )
        response = {
            "id": task.id,
            "status": url_for("api_task.status", task_id=task.id),
        }
    else:
        response = {}
        for channel in Channel.query.all():
            expiration = channel.expiration
            if expiration is None:
                # Expiration is not available yet (Channel just init)
                # Set ETA to four days later

                # eta = datetime.now() + timedelta(days=4)
                countdown = 60 * 60 * 24 * 4
            elif expiration > datetime.now() + timedelta(days=1):
                # Expiration is more than one day
                # Set ETA to one day before expiration

                # eta = expiration - timedelta(days=1)
                countdown = expiration - timedelta(days=1) - datetime.now()
                countdown = countdown.total_seconds()
            else:
                # Expiration is less than one day
                # Set ETA to now

                # eta = datetime.now()
                countdown = 0
            if execution == -2 and countdown > 0:
                countdown = randrange(int(countdown))
            task = renew_channels.apply_async(
                args=[[channel.id], interval],
                countdown=countdown,
                task_id=f"renew_{channel.id}_{str(uuid4())[:8]}",
            )
            response[channel.id] = task.id
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
