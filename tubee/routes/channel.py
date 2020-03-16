"""Channel Related Routes"""
import bs4
import pyrfc3339
from datetime import datetime, timedelta
from flask import (
    Blueprint,
    current_app,
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
    videos = build_youtube_api().search().list(part="snippet",
                                               channelId=channel_id,
                                               maxResults=50,
                                               order="date",
                                               type="video").execute()["items"]
    for video in videos:
        video["snippet"]["publishedAt"] = pyrfc3339.parse(
            video["snippet"]["publishedAt"])
        base_thumbnails_url = "/".join(
            video["snippet"]["thumbnails"]["high"]["url"].split("/")[:-1])
        video["snippet"]["thumbnails"]["standard"] = {
            "url": base_thumbnails_url + "/sddefault.jpg",
            "width": 640,
            "height": 480
        }
        video["snippet"]["thumbnails"]["maxres"] = {
            "url": base_thumbnails_url + "/maxresdefault.jpg",
            "width": 1280,
            "height": 720
        }
        callback_search = Callback.query.filter_by(
            channel_id=channel_id,
            type="Hub Notification",
            video_id=video["id"]["videoId"]).order_by(
                Callback.timestamp.asc()).all()
        video["snippet"]["callback"] = {
            "datetime":
            callback_search[0].timestamp
            if bool(callback_search) else "",
            "count":
            len(callback_search)
        }
    actions = current_user.subscriptions.filter_by(
        channel_id=channel_id).first().actions.all()
    form = ActionForm()
    return render_template("channel.html",
                           channel=channel_item,
                           videos=videos,
                           actions=actions,
                           form=form)


@channel_blueprint.route("/subscribe", methods=["GET", "POST"])
@login_required
def subscribe():
    """
    Page To Add Subscription
    (1) Request form with GET request
    (2) Submit the form POST request
    """
    if request.method == "GET":
        return render_template("subscribe.html")
    if request.method == "POST":
        if current_user.subscribe_to(request.form["channel_id"]):
            flash("Subscribe Success", "success")
        else:
            flash("Oops! Subscribe Failed for some reason", "danger")
        return redirect(url_for("main.dashboard"))


# TODO: REBUILD THIS DAMN MESSY ROUTE
@channel_blueprint.route("/<channel_id>/callback", methods=["GET", "POST"])
def callback(channel_id):
    """
    GET: Receive Hub Challenges to maintain subscription
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
        else:
            response = callback_item.type = "Unknown GET Request"
    elif request.method == "POST":
        # Preprocessing
        test_mode = bool("testing" in request.args.to_dict())
        post_datas = request.get_data().decode("utf-8")
        soup = bs4.BeautifulSoup(post_datas, "xml")
        # TODO: Inspecting
        try:
            video_id = soup.find("yt:videoId").string
        except Exception as error:
            current_app.logger.info(
                "Video ID not Found for {}".format(callback_item))
            current_app.logger.info(error)
            current_app.logger.info(soup)

        # Update Database Records
        video_item = Video.query.get(video_id)
        new_video = not bool(video_item)
        if new_video:
            video_item = Video(video_id, channel_item)
        video_item.callbacks.append(callback_item)
        callback_item.video = video_item
        callback_item.type = "Hub Notification"
        infos["data"] = post_datas

        # Fetch Video Infos
        # video_title = soup.entry.find("title").string
        # video_datetime = parser.parse(
        #     soup.entry.find("published").string).replace(tzinfo=None)
        # video_infos = build_youtube_api().videos().list(
        #     part="snippet", id=video_id).execute()["items"][0]["snippet"]
        # video_description = video_item.details["snippet"]["description"]
        # video_thumbnails = video_item.details["snippet"]["thumbnails"]["medium"]["url"]
        # previous_callback = Callback.query.filter_by(
        #     video_id=video_id).count() - 1  # Don't count this callback
        # new_video_update = bool(previous_callback)
        try:  # TODO
            video_file_url = youtube_dl.fetch_video_metadata(video_id)["url"]
        except Exception as e:
            video_file_url = None

        # List users
        response = {}
        for sub in Subscription.query.filter_by(channel_id=channel_id).all():
            # old_video_update = bool(
            #     video_datetime < sub.subscribe_timestamp)
            # current_app.logger.info(
            #     "New Video Update: {}".format(new_video_update))
            # current_app.logger.info(
            #     "Old Video Update: {}".format(old_video_update))
            # current_app.logger.info(
            #     "Action as Test Mode: {}".format(test_mode))
            # current_app.logger.info("Subscriber is Admin: {}".format(
            #     sub.user.admin))

            # Decide to Run or Not
            if test_mode and sub.user.admin:
                current_app.logger.info("Test Callback Pass")
                pass
            elif not new_video:
                continue
            # elif old_video_update or new_video_update:
            #     continue

            # Execute Actions
            response[sub.username] = {}
            for action in sub.actions:
                try:
                    results = action.execute(
                        video_id=video_id,
                        video_title=video_item.name,
                        video_description=video_item.details["snippet"]
                        ["description"],
                        video_thumbnails=video_item.details["snippet"]
                        ["thumbnails"]["medium"]["url"],
                        video_file_url=video_file_url,
                        channel_name=channel_item.name)
                except Exception as error:
                    results = error
                current_app.logger.info("{}-{}: {}".format(
                    sub.username, action.id, results))
                response[sub.username][action.id] = str(results)

        # Auto Renew if expiration is close
        expiration = channel_item.expiration
        if expiration and expiration - datetime.now() < timedelta(days=2):
            response["renew"] = channel_item.renew()
            current_app.logger.info("Channel renewed during callback")
            current_app.logger.info(response["renew"])
            notify_admin("Deployment",
                         "Pushover",
                         message="{} <{}>".format(channel_item.name,
                                                  channel_item.id),
                         title="Channel renewed during callback")
        response = jsonify(response)
    callback_item.infos = infos
    db.session.commit()
    return response
