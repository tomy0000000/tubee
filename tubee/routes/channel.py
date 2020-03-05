"""Channel Related Routes"""
import bs4
import pyrfc3339
from datetime import datetime, timedelta
from dateutil import parser
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
from ..helper import youtube_dl
from ..helper.youtube import build_youtube_api
from ..models import Callback, Channel, Subscription
channel_blueprint = Blueprint("channel", __name__)


@channel_blueprint.route("/<channel_id>")
def channel(channel_id):
    channel_item = Channel.query.filter_by(
        channel_id=channel_id).first_or_404()
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
            action="Hub Notification",
            details=video["id"]["videoId"]).order_by(
                Callback.received_datetime.asc()).all()
        video["snippet"]["callback"] = {
            "datetime":
            callback_search[0].received_datetime
            if bool(callback_search) else "",
            "count":
            len(callback_search)
        }
    actions = current_user.subscriptions.filter_by(
        subscribing_channel_id=channel_id).first().actions.all()
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
@channel_blueprint.route("/unsubscribe/<channel_id>", methods=["GET", "POST"])
@login_required
def unsubscribe(channel_id):
    """
    Page To Unsubscribe
    (1) Request confirmation with GET request
    (2) Submit the form POST request
    """
    subscription = current_user.subscriptions.filter_by(
        subscribing_channel_id=channel_id).first()
    if subscription is None:
        flash(
            "You can't unsubscribe to {} since you havn't subscribe to it.".
            format(channel_id), "warning")
    if request.method == "GET":
        return render_template("unsubscribe.html",
                               channel_name=subscription.channel.channel_name)
    if request.method == "POST":
        if current_user.unbsubscribe(channel_id):
            flash("Unsubscribe Success", "success")
        else:
            flash("Oops! Unsubscribe Failed for some reason", "danger")
    return redirect(url_for("main.dashboard"))


# TODO: REBUILD THIS DAMN MESSY ROUTE
@channel_blueprint.route("/<channel_id>/callback", methods=["GET", "POST"])
def callback(channel_id):
    """
    GET: Receive Hub Challenges to maintain subscription
    POST: New Update from Hub
    """
    channel_item = Channel.query.filter_by(
        channel_id=channel_id).first_or_404()
    callback_item = Callback(channel_item)
    callback_item.method = request.method
    callback_item.path = request.path
    callback_item.arguments = request.args
    callback_item.user_agent = str(request.user_agent)
    try:
        if request.method == "GET":
            get_args = request.args.to_dict()
            response = get_args.get("hub.challenge")
            if response:
                callback_item.action = "Hub Challenge"
                callback_item.details = response
            else:
                callback_item.action = "Unknown GET Request"
        elif request.method == "POST":
            test_mode = bool("testing" in request.args.to_dict())
            post_datas = request.get_data()
            soup = bs4.BeautifulSoup(post_datas, "xml")
            video_id = soup.find("yt:videoId").string
            video_title = soup.entry.find("title").string
            published_datetime = parser.parse(
                soup.entry.find("published").string).replace(tzinfo=None)

            video_infos = build_youtube_api().videos().list(
                part="snippet", id=video_id).execute()
            video_description = video_infos["items"][0]["snippet"][
                "description"]
            video_thumbnails = video_infos["items"][0]["snippet"][
                "thumbnails"]["medium"]["url"]

            # TODO
            try:
                video_file_url = youtube_dl.fetch_video_metadata(
                    video_id)["url"]
            except Exception as e:
                video_file_url = None

            # Append Callback SQL Record
            callback_item.action = "Hub Notification"
            callback_item.details = video_id
            callback_item.data = post_datas
            """
            1. List Users who subscribe to this channel
            (for each user)
            2. List Actions which should be execute
            3. Execute Actions
            """
            subs = Subscription.query.filter_by(
                subscribing_channel_id=channel_id).all()
            current_app.logger.info(Callback.query.filter_by(details=video_id).count() - 1)
            new_video_update = bool(
                Callback.query.filter_by(details=video_id).count() - 1)  # Don't count this callback
            response = {}
            for sub in subs:
                old_video_update = bool(
                    published_datetime < sub.subscribe_datetime)
                current_app.logger.info(
                    "New Video Update: {}".format(new_video_update))
                current_app.logger.info(
                    "Old Video Update: {}".format(old_video_update))
                current_app.logger.info(
                    "Action as Test Mode: {}".format(test_mode))
                current_app.logger.info("Subscriber is Admin: {}".format(
                    sub.subscriber.admin))
                # Decide to Pass or Not
                if test_mode and sub.subscriber.admin:
                    pass
                elif old_video_update or new_video_update:
                    continue

                # Subscription Action
                response[sub.subscriber.username] = {}
                for action in sub.actions:
                    try:
                        results = action.execute(
                            video_id=video_id,
                            video_title=video_title,
                            video_description=video_description,
                            video_thumbnails=video_thumbnails,
                            video_file_url=video_file_url,
                            channel_name=channel_item.channel_name)
                        current_app.logger.info("{}-{}: OK".format(
                            sub.subscriber_username, action.action_id))
                    except Exception as error:
                        current_app.logger.info("{}-{}: {}".format(
                            sub.subscriber_username, action.action_id, error))
                        results = error
                    response[sub.subscriber_username][action.action_id] = str(
                        results)

            # Auto Renew if expiration is close
            if channel_item.expire_datetime and channel_item.expire_datetime - datetime.now() < timedelta(
                    days=2):
                response["renew"] = channel_item.renew()
                current_app.logger.info("Channel renewed during callback")
                current_app.logger.info(response["renew"])
                notify_admin("Deployment",
                             "Pushover",
                             message="{} <{}>".format(
                                 channel_item.channel_name,
                                 channel_item.channel_id),
                             title="Channel renewed during callback")
            response = jsonify(response)
    except Exception as error:
        current_app.logger.info("Unexpected Error")
        current_app.logger.info(error)
    finally:
        db.session.commit()
    return response
