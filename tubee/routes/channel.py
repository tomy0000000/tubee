"""Channel Related Routes"""
import bs4
import pyrfc3339
import youtube_dl
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
from ..helper.youtube import build_youtube_api
from ..models import ActionEnum, Callback, Channel, Subscription
channel_blueprint = Blueprint("channel", __name__)
youtube_dl_service = youtube_dl.YoutubeDL({
    "skip_download": True,
    "ignoreerrors": True,
    "extract_flat": True,
    "playlistend": 30
})


@channel_blueprint.route("/<channel_id>")
def channel(channel_id):
    channel_item = Channel.query.filter_by(
        channel_id=channel_id).first_or_404()
    # videos = build_youtube_api().search().list(part="snippet",
    #                                            channelId=channel_id,
    #                                            maxResults=50,
    #                                            order="date",
    #                                            type="video").execute()["items"]
    # for video in videos:
    #     video["snippet"]["publishedAt"] = pyrfc3339.parse(
    #         video["snippet"]["publishedAt"])
    #     base_thumbnails_url = "/".join(
    #         video["snippet"]["thumbnails"]["high"]["url"].split("/")[:-1])
    #     video["snippet"]["thumbnails"]["standard"] = {
    #         "url": base_thumbnails_url + "/sddefault.jpg",
    #         "width": 640,
    #         "height": 480
    #     }
    #     video["snippet"]["thumbnails"]["maxres"] = {
    #         "url": base_thumbnails_url + "/maxresdefault.jpg",
    #         "width": 1280,
    #         "height": 720
    #     }
    #     callback_search = Callback.query.filter_by(
    #         channel_id=channel_id,
    #         action="Hub Notification",
    #         details=video["id"]["videoId"]).order_by(
    #             Callback.received_datetime.asc()).all()
    #     video["snippet"]["callback"] = {
    #         "datetime":
    #         callback_search[0].received_datetime
    #         if bool(callback_search) else "",
    #         "count":
    #         len(callback_search)
    #     }
    actions = current_user.subscriptions.filter_by(
        subscribing_channel_id=channel_id).first().actions.all()
    form = ActionForm()
    form.action_type.choices = [(item.name, item.value) for item in ActionEnum]
    return render_template("channel.html",
                           channel=channel_item,
                           # videos=videos,
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
    if request.method == "GET":
        get_args = request.args.to_dict()
        response = get_args.pop("hub.challenge", "Error")
        new_callback = Callback(channel_item, "Unknown GET Request" \
                                if response == "Error" else "Hub Challenge", response,
                                request.method, request.path, request.args,
                                request.data, str(request.user_agent))
    elif request.method == "POST":
        test_mode = bool("testing" in request.args.to_dict())
        post_datas = request.get_data()
        soup = bs4.BeautifulSoup(post_datas, "xml")
        video_id = soup.find("yt:videoId").string
        video_title = soup.entry.find("title").string
        published_datetime = parser.parse(
            soup.entry.find("published").string).replace(tzinfo=None)

        video_infos = build_youtube_api().videos().list(part="snippet",
                                                        id=video_id).execute()
        video_description = video_infos["items"][0]["snippet"]["description"]
        video_thumbnails = video_infos["items"][0]["snippet"]["thumbnails"][
            "medium"]["url"]

        # Append Callback SQL Record
        new_callback = Callback(channel_item, "Hub Notification", video_id,
                                request.method, request.path, request.args,
                                request.data, str(request.user_agent))
        """
        1. List Users who subscribe to this channel
        (for each user)
        2. List Actions which should be execute
        3. Execute Actions
        """

        # Decide to Pass or Not
        subs = Subscription.query.filter_by(subscribing_channel_id=channel_id)
        new_video_update = bool(
            Callback.query.filter_by(details=video_id).count())
        response = {"append_wl_to": {}, "notification_to": {}}
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
            if test_mode and sub.subscriber.admin:
                pass
            elif old_video_update or new_video_update:
                return jsonify(None)

            # # Append to WL
            # if proceed_add_playlist:
            #     try:
            #         response = sub.subscriber.insert_video_to_playlist(video_id)
            #     except RuntimeError as error:
            #         response = error.args[0]
            #     response["append_wl_to"][sub.subscriber_username] = response
            # current_app.logger.info(
            #     "Playlist Appended: {}".format(proceed_add_playlist))

            # Push Notification
            # if proceed_notification:
            #     ntf = sub.subscriber.send_notification(
            #         "Callback",
            #         "Pushover",
            #         message="{}\n{}".format(
            #             video_title, video_description),
            #         title="New from {}".format(
            #             sub.channel.channel_name),
            #         url="https://www.youtube.com/watch?v={}".format(video_id),
            #         url_title=video_title,
            #         image=video_thumbnails)
            #     response["notification_to"][
            #         sub.subscriber_username] = ntf
            #     current_app.logger.info(ntf)
            # current_app.logger.info(
            #     "Notification Send: {}".format(proceed_notification))
            # current_app.logger.info("------------------------")

            # Subscription Action
            for action in sub.actions:
                action.execute(
                    video_id=video_id,
                    message=video_title,
                    # message="{}\n{}".format(video_title, video_description),
                    title="New from {}".format(sub.channel.channel_name),
                    url="https://www.youtube.com/watch?v={}".format(video_id),
                    url_title=video_title,
                    image=video_thumbnails,
                )

        response = jsonify(response)

    db.session.add(new_callback)
    try:
        db.session.commit()
    except Exception as error:
        current_app.logger.error("SQL Commit Failed")
    return response
