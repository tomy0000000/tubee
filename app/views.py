"""Views for Tubee"""
from datetime import datetime, timedelta
import rfc3339
import requests
import google_auth_oauthlib.flow
import google.oauth2.credentials
from apiclient import discovery
from dateutil import parser
from flask import redirect, request, render_template, url_for, session, current_app
from flask_login import current_user, login_required

from . import login_manager, db, bcrypt
from .routes.main import main as route_blueprint
from .helper import build_youtube_service
from .models import User, Callback, Subscription

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

#     #       #######  #####  ### #     #
#     #       #     # #     #  #  ##    #
#     #       #     # #        #  # #   #
#     #       #     # #  ####  #  #  #  #
#     #       #     # #     #  #  #   # #
#     #       #     # #     #  #  #    ##
#     ####### #######  #####  ### #     #

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return render_template("empty.html", info="You Must Login First!")

@route_blueprint.route("/renew-password")
@login_required
def login_renew_password():
    current_user.password = bcrypt.generate_password_hash(current_user.password)
    db.session.commit()
    return render_template("empty.html", info="Done")

@route_blueprint.route('/login/youtube/authorize')
@login_required
def login_youtube_authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        current_app.instance_path + "beta_client_secret.json",
        scopes="https://www.googleapis.com/auth/youtube.force-ssl")
    flow.redirect_uri = url_for("main.login_youtube_oauth_callback", _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes="true")

    # Store the state so the callback can verify the auth server response.
    session["state"] = state
    return redirect(authorization_url)

@route_blueprint.route("/login/youtube/oauth_callback")
@login_required
def login_youtube_oauth_callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session["state"]

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        current_app.instance_path + "beta_client_secret.json",
        scopes="https://www.googleapis.com/auth/youtube.force-ssl",
        state=state)
    flow.redirect_uri = url_for("main.login_youtube_oauth_callback", _external=True)
    flow.fetch_token(authorization_response=request.url)
    credentials_dict = {
        "token": flow.credentials.token,
        "refresh_token": flow.credentials.refresh_token,
        "token_uri": flow.credentials.token_uri,
        "client_id": flow.credentials.client_id,
        "client_secret": flow.credentials.client_secret,
        "scopes": flow.credentials.scopes
    }
    current_user.youtube_credentials = credentials_dict
    session["credentials"] = credentials_dict

    # return redirect(url_for("main.login_setting"))
    return render_template("setting.html", user=current_user, notes=credentials_dict)

@route_blueprint.route("/login/youtube/revoke")
@login_required
def login_youtube_revoke():
    if not current_user.youtube_credentials:
        return render_template("empty.html", info="Credentials not set")
    credentials = google.oauth2.credentials.Credentials(**current_user.youtube_credentials)
    response = requests.post("https://accounts.google.com/o/oauth2/revoke",
                             params={"token": credentials.token},
                             headers={"content-type": "application/x-www-form-urlencoded"})
    if response.status_code == 200:
        current_user.youtube_credentials = {}
    # return redirect(url_for("main.login_setting"))
    return render_template("setting.html", user=current_user, notes=[response.status_code, response.text])

#     #     #
#     #     # #    # #####
#     #     # #    # #    #
#     ####### #    # #####
#     #     # #    # #    #
#     #     # #    # #    #
#     #     #  ####  #####

@route_blueprint.route("/hub/history")
def hub_history():
    """List all callback history of all channel"""
    callbacks = Callback.query.order_by(Callback.received_datetime.desc()).all()
    return render_template("hub_history.html", callbacks=callbacks)

@route_blueprint.route("/hub/history/<channel_id>")
def hub_history_channel(channel_id):
    """List all callback history of a specific channel"""
    callbacks = Callback.query.filter_by(
        channel_id=channel_id).order_by(Callback.received_datetime.desc()).all()
    subscription = Subscription.query.filter(Subscription.channel_id == channel_id).first_or_404()
    return render_template("hub_history.html",
                           callbacks=callbacks,
                           channel_name=subscription.channel_name)

@route_blueprint.route("/hub/status")
def hub_status():
    channels = Subscription.query.order_by(Subscription.channel_name).all()
    return render_template("status.html", channels=channels)

@route_blueprint.route("/hub/renew/<channel_id>")
def hub_renew_channel(channel_id):
    subscription = Subscription.query.filter(Subscription.channel_id == channel_id).first_or_404()
    code = subscription.renew_hub().status_code
    return render_template("empty.html", info="Response HTTP Status Code: {status_code}".format(
        status_code=code))

@route_blueprint.route("/hub/renew")
def hub_renew():
    response = {}
    for subscription in Subscription.query.filter(Subscription.active):
        response[subscription.channel_id] = subscription.renew_hub().status_code
    return render_template("empty.html", info=response)

#     ######
#     #     # #    #  ####  #    #  ####  #    # ###### #####
#     #     # #    # #      #    # #    # #    # #      #    #
#     ######  #    #  ####  ###### #    # #    # #####  #    #
#     #       #    #      # #    # #    # #    # #      #####
#     #       #    # #    # #    # #    #  #  #  #      #   #
#     #        ####   ####  #    #  ####    ##   ###### #    #

@route_blueprint.route("/pushover/push", methods=["GET", "POST"])
@login_required
def pushover_push():
    if request.method == "GET":
        return render_template("pushover_push.html")
    elif request.method == "POST":
        form_datas = request.form
        response = current_user.send_notification("Test", form_datas["message"], title=form_datas["title"])
        return render_template("empty.html", info=response)
    response = "Something Went Wrong!!!!"
    return render_template("empty.html", info=response)

#     #     #               #######
#      #   #   ####  #    #    #    #    # #####  ######
#       # #   #    # #    #    #    #    # #    # #
#        #    #    # #    #    #    #    # #####  #####
#        #    #    # #    #    #    #    # #    # #
#        #    #    # #    #    #    #    # #    # #
#        #     ####   ####     #     ####  #####  ######

@route_blueprint.route("/youtube/video")
def youtube_video():
    videos = []
    for channel in Subscription.query.filter_by(active=True):
        videos += list_channel_videos(channel.channel_id)
    videos.sort(key=lambda x: parser.parse(x["snippet"]["publishedAt"]), reverse=True)
    for video in videos:
        video_search = Callback.query.filter_by(
            channel_id=video["snippet"]["channelId"],
            action_type="Hub Notification",
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
        channel["status"] = bool(Subscription.query.filter_by(
            channel_id=channel["snippet"]["resourceId"]["channelId"]).count())
    return render_template("youtube_subscription_page.html", **datas)

@route_blueprint.route("/youtube/playlist_insert/<video_id>")
@login_required
def youtube_playlist_insert(video_id):
    return render_template("empty.html", info=current_user.insert_video_to_playlist(video_id))

#     ######
#     #     # ###### #####  #  ####
#     #     # #      #    # # #
#     ######  #####  #    # #  ####
#     #   #   #      #    # #      #
#     #    #  #      #    # # #    #
#     #     # ###### #####  #  ####

# @route_blueprint.route("/redis/set/<key>/<value>")
# def redis_write(key, value):
#     response = redis_store.set(key, value)
#     return render_template("empty.html", info=response)
#
# @route_blueprint.route("/redis/get/<key>")
# def redis_read(key):
#     response = redis_store.get(key)
#     return render_template("empty.html", info=response)

#     ######
#     #     #  ####  #    # ##### ######  ####
#     #     # #    # #    #   #   #      #
#     ######  #    # #    #   #   #####   ####
#     #   #   #    # #    #   #   #           #
#     #    #  #    # #    #   #   #      #    #
#     #     #  ####   ####    #   ######  ####

@route_blueprint.route("/channel/oldsummary/<channel_id>")
def summary_channel(channel_id):
    subscription = Subscription.query.filter(Subscription.channel_id == channel_id).first_or_404()
    videos = list_channel_videos(channel_id)
    for video in videos:
        video_search = Callback.query.filter_by(
            channel_id=channel_id,
            action_type="Hub Notification",
            details=video["id"]["videoId"]).order_by(Callback.received_datetime.asc()
                                                    ).all()
        video["callback"] = {
            "datetime": video_search[0].received_datetime if len(video_search) > 0 else "",
            "count": len(video_search)
        }
        # video["callback"]["datetime"] = video_search
        # video["callback"]["count"] = len(video_search)
        # video["callback"]["datetime"] = video_search[0]["received_datetime"]
        # video["callback"]["count"] = len(video_search)
    return render_template("summary.html", videos=videos, channel_name=subscription.channel_name)
