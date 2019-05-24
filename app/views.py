"""Views for Tubee"""
from datetime import datetime, timedelta

import rfc3339
from apiclient import discovery
from flask import request, render_template, current_app
from flask_login import current_user, login_required
from . import scheduler
from .routes.main import main as route_blueprint
from .helper import build_youtube_public_service, build_youtube_service
from .models import Callback, Channel

#     #######
#     #       #    # #    #  ####   ####
#     #       #    # ##   # #    # #
#     #####   #    # # #  # #       ####
#     #       #    # #  # # #           #
#     #       #    # #   ## #    # #    #
#     #        ####  #    #  ####   ####

def list_channel_videos(channel_id, recent=True):
    results = []
    response = {"nextPageToken": ""}
    while "nextPageToken" in response:
        YouTube_Service_Public = discovery.build(
            current_app.config["YOUTUBE_API_SERVICE_NAME"],
            current_app.config["YOUTUBE_API_VERSION"],
            cache_discovery=False,
            developerKey=current_app.config["YOUTUBE_API_DEVELOPER_KEY"])
        response = YouTube_Service_Public.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50,
            order="date",
            pageToken=response["nextPageToken"],
            publishedAfter=rfc3339.rfc3339(datetime.now()-timedelta(days=2)) if recent else None,
            type="video",
            fields="items(etag,id/videoId,snippet(publishedAt,thumbnails/default,title))"
        ).execute()
        for video in response["items"]:
            video["snippet"]["channelId"] = channel_id
        results += response["items"]
    return results

#     #     #
#     #     # #    # #####
#     #     # #    # #    #
#     ####### #    # #####
#     #     # #    # #    #
#     #     # #    # #    #
#     #     #  ####  #####

@route_blueprint.route("/hub/status")
def hub_status():
    channels = Channel.query.order_by(Channel.channel_name).all()
    return render_template("status.html", channels=channels)

@route_blueprint.route("/hub/renew")
def hub_renew():
    response = {}
    for channel in Channel.query.filter(Channel.active):
        response[channel.channel_id] = channel.renew_hub()
    return render_template("empty.html", info=response)

def test_func():
    print("Hello")

@route_blueprint.route("/regist_job")
def reg_job():
    response = scheduler.add_job("test", test_func, trigger="interval", seconds=2)
    return render_template("empty.html", info=response)

#     #     #               #######
#      #   #   ####  #    #    #    #    # #####  ######
#       # #   #    # #    #    #    #    # #    # #
#        #    #    # #    #    #    #    # #####  #####
#        #    #    # #    #    #    #    # #    # #
#        #    #    # #    #    #    #    # #    # #
#        #     ####   ####     #     ####  #####  ######

@route_blueprint.route("/channel/oldsummary/<channel_id>")
def summary_channel(channel_id):
    subscription = Channel.query.filter(Channel.channel_id == channel_id).first_or_404()
    videos = list_channel_videos(channel_id)
    for video in videos:
        video_search = Callback.query.filter_by(
            channel_id=channel_id,
            action="Hub Notification",
            details=video["id"]["videoId"]).order_by(Callback.received_datetime.asc()
                                                    ).all()
        video["callback"] = {
            "datetime": video_search[0].received_datetime if len(video_search) > 0 else "",
            "count": len(video_search)
        }
    return render_template("summary.html", videos=videos, channel_name=subscription.channel_name)

@route_blueprint.route("/channel/fixed-oldsummary/<channel_id>")
def fixed_summary_channel(channel_id):
    channel = Channel.query.filter_by(channel_id=channel_id).first_or_404()
    service = build_youtube_public_service()
    videos = service.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=50,
        order="date",
        type="video",
        fields="items(etag,id/videoId,snippet(publishedAt,thumbnails/default,title))"
    ).execute()["items"]
    for video in videos:
        video["snippet"]["channelId"] = channel_id
        video_search = Callback.query.filter_by(
            channel_id=channel_id,
            action="Hub Notification",
            details=video["id"]["videoId"]).order_by(Callback.received_datetime.asc()
                                                    ).all()
        video["callback"] = {
            "datetime": video_search[0].received_datetime if bool(video_search) else "",
            "count": len(video_search)
        }
    return render_template("summary.html", videos=videos, channel_name=channel.channel_name)

@route_blueprint.route("/youtube/video")
def youtube_video():
    videos = []
    for channel in Channel.query.filter_by(active=True):
        videos += list_channel_videos(channel.channel_id)
    for video in videos:
        video_search = Callback.query.filter_by(
            channel_id=video["snippet"]["channelId"],
            action="Hub Notification",
            details=video["id"]["videoId"]).order_by(Callback.received_datetime.asc()
                                                    ).all()
        video["callback"] = {
            "datetime": video_search[0].received_datetime if len(video_search) > 0 else "",
            "count": len(video_search)
        }
    return render_template("youtube_video.html", videos=videos)

@route_blueprint.route("/youtube/subscription")
@login_required
def youtube_subscription():
    get_params = request.args.to_dict()
    datas = {}

    # Mode
    if "list_all" in get_params:
        datas["channels"] = []
        response = {"nextPageToken": ""}
        youtube_service = build_youtube_service(current_user.youtube_credentials)
        while "nextPageToken" in response:
            response = youtube_service.subscriptions().list(
                part="snippet",
                maxResults=50,
                mine=True,
                order="alphabetical",
                pageToken=response["nextPageToken"]
            ).execute()
            datas["channels"] += response["items"]
        datas["list_all"] = True
    else:
        page_token = get_params.pop("page_token", None)
        youtube_service = build_youtube_service(current_user.youtube_credentials)
        response = youtube_service.subscriptions().list(
            part="snippet",
            maxResults=25,
            mine=True,
            order="alphabetical",
            pageToken=page_token
        ).execute()
        datas["channels"] = response["items"]
        datas["prev_page"] = response.pop("prevPageToken", None)
        datas["next_page"] = response.pop("nextPageToken", None)
    for channel in datas["channels"]:
        channel["status"] = bool(Channel.query.filter_by(
            channel_id=channel["snippet"]["resourceId"]["channelId"]).count())
    return render_template("youtube_subscription_page.html", **datas)
