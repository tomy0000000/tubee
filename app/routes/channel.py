"""Channel Related Routes"""
import json
from datetime import datetime

import bs4
import pyrfc3339
import youtube_dl
from apiclient.errors import HttpError
from dateutil import parser
from flask import Blueprint, current_app, jsonify, render_template, request
from flask_login import current_user, login_required
from .. import db
from ..helper import send_notification, build_youtube_public_service
from ..models import Callback, Channel, User, UserSubscription
channel_blueprint = Blueprint("channel", __name__)
youtube_dl_service = youtube_dl.YoutubeDL({
    "skip_download": True,
    "ignoreerrors": True,
    "extract_flat": True,
    "playlistend": 30
})

@channel_blueprint.route("/<channel_id>")
def channel(channel_id):
    #
    # Avatar                    Channel Name
    # Avatar                    Channel ID
    #
    # State                                   Expiration
    # Last Notification                       Last Notification Error
    # Last Challenge                          Last Challenge Error
    # Last Subscribe / Last Unsubscribe       Stat
    # 
    # Channel Videos
    # 
    # video_img     video_title         published_datetime    callback_dt
    #               (msg_box: video_id)                 (msg_box: callback_cnt)
    #                                                   (float: callback / notification detail)
    # 
    # (dynamic loading)

    # TODO: Support New Un-Subscribed Channel
    channel_item = Channel.query.filter_by(channel_id=channel_id).first_or_404()
    # url = "https://www.youtube.com/channel/{channel_id}/videos".format(channel_id=channel_id)
    # channel_metadatas = youtube_dl_service.extract_info(url)
    # videos = youtube_dl_service.extract_info(channel_metadatas["url"])
    service = build_youtube_public_service()
    videos = service.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=50,
        order="date",
        type="video"
    ).execute()["items"]
    for video in videos:
        # video["snippet"]["channelId"] = channel_id
        video["snippet"]["publishedAt"] = pyrfc3339.parse(video["snippet"]["publishedAt"])
        video_search = Callback.query.filter_by(
            channel_id=channel_id,
            action="Hub Notification",
            details=video["id"]["videoId"]).order_by(Callback.received_datetime.asc()
                                                    ).all()
        video["callback"] = {
            "datetime": video_search[0].received_datetime if bool(video_search) else "",
            "count": len(video_search)
        }
    return render_template("channel.html", channel=channel_item, videos=videos)

# TODO: REBUILD THIS DAMN MESSY ROUTE
@channel_blueprint.route("/subscribe", methods=["GET", "POST"])
@login_required
def subscribe():
    """
    Page To Add Subscription
    (1) Request form with GET request
    (2) Submit the form POST request
    """
    if request.method == "GET":
        prefilled = request.args["channelid"] if "channelid" in request.args else None
        return render_template("subscribe.html", prefilled=prefilled)
    if request.method == "POST":

        # Build Subscription
        channel_id = request.form["channel_id"]
        channel = Channel.query.get(channel_id)
        if not channel:
            channel = Channel(channel_id)
            db.session.add(channel)
            try:
                db.session.commit()
            except Exception as error:
                current_app.logger.error("SQL Commit Failed")
        
        # Schedule renew datetime
        # job_response = scheduler.add_job(
        #     id="renew_"+channel_id,
        #     func=renew_subscription,
        #     trigger="interval",
        #     args=[new_subscription],
        #     days=4)

        current_user.subscribe_to(channel)
        response = {
            # "Renew Jobs": job_response,
            "HTTP Status Code": channel.activate_response.status_code
        }
        return render_template("empty.html", info=response)

# TODO: REBUILD THIS DAMN MESSY ROUTE
@channel_blueprint.route("/unsubscribe/<channel_id>", methods=["GET", "POST"])
@login_required
def unsubscribe(channel_id):
    """
    Page To Ubsubscribe
    (1) Request confirmation with GET request
    (2) Submit the form POST request
    """
    channel = Channel.query.filter_by(channel_id=channel_id).first_or_404()
    if request.method == "GET":
        response_page = render_template("unsubscribe.html", channel_name=channel.channel_name)
    elif request.method == "POST":
        response = channel.deactivate()
        current_app.logger.info(response)
        response_page = render_template("empty.html", info=response)
    return response_page


# TODO: REBUILD THIS DAMN MESSY ROUTE
@channel_blueprint.route("/<channel_id>/callback", methods=["GET", "POST"])
def callback(channel_id):
    """
    GET: Receive Hub Challenges to maintain subscription
    POST: New Update from Hub
    """
    if request.method == "GET":
        get_args = request.args.to_dict()
        response = get_args.pop("hub.challenge", "Error")
        new_callback = Callback(channel_id, "Unknown GET Request" \
                                if response == "Error" else "Hub Challenge", response,
                                request.method, request.path, request.args,
                                request.data, request.user_agent)
    elif request.method == "POST":
        test_mode = bool("testing" in request.args.to_dict())
        post_datas = request.get_data()
        soup = bs4.BeautifulSoup(post_datas, "xml")
        video_id = soup.find("yt:videoId").string
        published_datetime = parser.parse(soup.entry.find("published").string).replace(tzinfo=None)

        # Append Callback SQL Record
        new_callback = Callback(channel_id, "Hub Notification", video_id,
                                request.method, request.path, request.args,
                                request.data, request.user_agent)

        """
        1. List Users who subscribe to this channel
        (for each user)
        2. List Actions which should be execute
        3. Execute Actions
        """

        # Decide to Pass or Not
        subscriptions = UserSubscription.query.filter_by(subscribing_channel_id=channel_id)
        new_video_update = bool(Callback.query.filter_by(details=video_id).count())
        response = {
            "append_wl_to": {},
            "notification_to": {}
        }
        for subscription in subscriptions:
            old_video_update = bool(published_datetime < subscription.subscribe_datetime)
            current_app.logger.info("New Video Update: {}".format(new_video_update))
            current_app.logger.info("Old Video Update: {}".format(old_video_update))
            current_app.logger.info("Action as Test Mode: {}".format(test_mode))
            current_app.logger.info("Subscriber is Admin: {}".format(subscription.subscriber.admin))
            proceed_add_playlist = proceed_notification = True
            if test_mode and subscription.subscriber.admin:
                pass
            elif old_video_update or new_video_update:
                proceed_add_playlist = proceed_notification = False
            # Append to WL
            if proceed_add_playlist:
                # TODO: Make Try/Except a part of user method
                try:
                    playlist_insert_response = subscription.subscriber.insert_video_to_playlist(video_id)
                    video_description = playlist_insert_response["snippet"]["description"]
                    video_thumbnails = playlist_insert_response["snippet"]["thumbnails"]["high"]["url"]
                except HttpError as error:
                    playlist_insert_response = json.loads(error.content)["error"]["message"]
                    current_app.logger.error("Faield to insert {} to {}'s playlist".format(video_id, subscription.subscriber_username))
                    current_app.logger.error(playlist_insert_response)
                    proceed_notification = False
                response["append_wl_to"][subscription.subscriber_username] = playlist_insert_response
                current_app.logger.info(playlist_insert_response)
            current_app.logger.info("Playlist Appended: {}".format(proceed_add_playlist))
            # Push Notification
            if proceed_notification:
                title = "New from " + subscription.channel.channel_name
                message = soup.entry.find("title").string + "\n" + video_description
                notification_response = subscription.subscriber.send_notification(
                    "Callback", message,
                    title=title,
                    url="https://www.youtube.com/watch?v="+video_id,
                    url_title=soup.entry.find("title").string,
                    image=video_thumbnails)
                response["notification_to"][subscription.subscriber_username] = notification_response
                current_app.logger.info(notification_response)
            current_app.logger.info("Notification Send: {}".format(proceed_notification))
            current_app.logger.info("------------------------")
            response = jsonify(response)
    db.session.add(new_callback)
    try:
        db.session.commit()
    except Exception as error:
        current_app.logger.error("SQL Commit Failed")
    return response
