"""Views for Tubee"""
import json
from datetime import datetime, timedelta
import bs4
import rfc3339
import requests
import google_auth_oauthlib.flow
import google.oauth2.credentials
from apiclient import discovery
from apiclient.errors import HttpError
from dateutil import parser
from flask import redirect, request, render_template, url_for, session, current_app
from flask_login import current_user, login_required
from . import login_manager, db, bcrypt, scheduler
from .routes.main import main as route_blueprint

from .helper import send_notification, build_youtube_service
from .models import User, Callback, Request, Subscription

#     #######
#     #       #    # #    #  ####   ####
#     #       #    # ##   # #    # #
#     #####   #    # # #  # #       ####
#     #       #    # #  # # #           #
#     #       #    # #   ## #    # #    #
#     #        ####  #    #  ####   ####

def request_hub_status(channel_id, callback_url, hub_secret=None):
    try:
        response = requests.get(
            url="https://pubsubhubbub.appspot.com/subscription-details",
            params={
                "hub.callback": callback_url,
                "hub.topic": "https://www.youtube.com/xml/feeds/videos.xml?channel_id=" + channel_id,
                "hub.secret": hub_secret
            }
        )
        return response
    except requests.exceptions.RequestException:
        return -1

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

def list_channel_newest_videos(channel_id):
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
            publishedAfter=rfc3339.rfc3339(datetime.now()-timedelta(days=2)),
            type="video"
        ).execute()
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

@route_blueprint.route("/hub/status_api/<channel_id>/")
def hub_status_api_channel(channel_id):
    data = request_hub_status(channel_id, request.url_root + channel_id + "/callback")
    return data.text

@route_blueprint.route("/hub/status_api_tmp/<channel_id>/")
def hub_status_api_tmp_channel(channel_id):
    data = request_hub_status(channel_id, request.url_root + channel_id + "/callback")
    return render_template("empty.html", info=data.__dict__)

@route_blueprint.route("/hub/status/<channel_id>")
def hub_status_channel(channel_id):
    """
    Fetch Subscription info from hub
    (The response html is broken, therefore is NOT support by lxml)
    """
    subscription = Subscription.query.filter(Subscription.channel_id == channel_id).first_or_404()
    response = request_hub_status(channel_id, request.url_root + channel_id + "/callback")
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    status = {
        "channel_id": channel_id,
        "channel_name": subscription.channel_name,
        "details": {}
    }
    for each in soup.find_all("dt"):
        val = each.next_sibling.next_sibling.string.strip("\n ")
        if each.string == "State":
            status["state"] = val
        else:
            status["details"][each.string] = val
    return render_template("status_detail.html", status=status)

@route_blueprint.route("/hub/renew-info/<channel_id>")
def hub_renew_info_channel(channel_id):
    subscription = Subscription.query.filter(Subscription.channel_id == channel_id).first_or_404()
    subscription.renew_info()
    return render_template("empty.html", info="Done")

@route_blueprint.route("/hub/renew-info")
def hub_renew_info():
    for subscription in Subscription.query.filter(Subscription.active):
        subscription.renew_info()
    return render_template("empty.html", info="Done")

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
        response = send_notification("Test", current_user, form_datas["message"], title=form_datas["title"])
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
    for channel in Subscription.query.filter(Subscription.active == True):
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

@route_blueprint.route("/summary/<channel_id>")
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

@route_blueprint.route("/<channel_id>/callback", methods=["GET", "POST"])
def channel_callback_entry(channel_id):
    """
    GET: Receive Hub Challenges to maintain subscription
    POST: New Update from Hub
    """
    if request.method == "GET":
        get_args = request.args.to_dict()
        response = get_args.pop("hub.challenge", "Error")
        new_callback = Callback(datetime.now(), channel_id, "Unknown GET Request" \
                                if response == "Error" else "Hub Challenge", response,
                                request.args, request.data, request.user_agent)
        db.session.add(new_callback)
    elif request.method == "POST":
        test_mode = bool("testing" in request.args.to_dict())
        post_datas = request.get_data()
        soup = bs4.BeautifulSoup(post_datas, "xml")
        video_id = soup.find("yt:videoId").string
        Tomy = User.query.filter_by(username="Tomy").first_or_404()

        # Append Callback SQL Record
        new_callback = Callback(datetime.now(), channel_id, "Hub Notification",
                                video_id, request.args, request.data, request.user_agent)
        new_request = Request(request.method, request.path, request.args,
                              request.data, request.user_agent, datetime.now())
        db.session.add(new_callback)
        db.session.add(new_request)
        try:
            db.session.commit()
        except Exception as e:
            send_notification("SQL Error", Tomy, str(datetime.now())+"\n"+str(e),
                              title="Tubee encontered a SQL Error!!")


        """
        1. List Users who subscribe to this channel
        (for each user)
        2. List Actions which should be execute
        3. Execute Actions
        """

        # Decide to Pass or Not
        subscription = Subscription.query.filter_by(channel_id=channel_id).first_or_404()
        published_dt = parser.parse(soup.entry.find("published").string).replace(tzinfo=None)
        prev_callback_count = Callback.query.filter(Callback.details.like(video_id)).count()
        already_pushed = bool(prev_callback_count > 1)
        old_update = bool(published_dt < subscription.subscribe_datetime)
        # not_pushing = already_pushed or old_update
        if test_mode:
            pass
        elif already_pushed:
            current_app.logger.info("Already Pushed")
            return str("pass")
        elif old_update:
            current_app.logger.info("Old Video Update")
            return str("pass")
        
        # Append to WL
        try:
            infos = Tomy.insert_video_to_playlist(video_id)
            response = infos["snippet"]["description"]
            image_url = infos["snippet"]["thumbnails"]["high"]["url"]
        except HttpError as error:
            response = json.loads(error.content)["error"]["message"]
            image_url = None

        # Push Notification
        title = "New from " + subscription.channel_name
        message = soup.entry.find("title").string + "\n" + response
        response = send_notification("Callback", Tomy, message,
                                     title=title,
                                     url="https://www.youtube.com/watch?v="+video_id,
                                     url_title=soup.entry.find("title").string,
                                     image=image_url)

    return str(response)
