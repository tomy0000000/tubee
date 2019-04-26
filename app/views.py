"""Views for Tubee"""

# import mod_wsgi
import json
import os
import pprint
import sys
from datetime import datetime, timedelta
import bs4
import rfc3339
import requests
import google_auth_oauthlib.flow
import google.oauth2.credentials
from apiclient.errors import HttpError
from dateutil import parser
from flask import redirect, request, render_template, url_for, session
from flask_login import current_user, login_user, logout_user, login_required
from . import app, login_manager, db, bcrypt, YouTube_Service_Public, scheduler
from .form import LoginForm
from .helper import send_notification, build_youtube_service
from .models import User, Callback, Request, Subscription, Notification

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
    return render_template("empty.html", content="You Must Login First!")

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            login_user(user)
            return redirect(url_for("dashboard"))
        error = "Invalid username or password."
    return render_template("login.html", form=form, error=error)

@app.route("/renew-password")
@login_required
def login_renew_password():
    current_user.password = bcrypt.generate_password_hash(current_user.password)
    db.session.commit()
    return render_template("empty.html", content="Done")

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/login/setting", methods=["GET", "POST"])
@login_required
def login_setting():
    notes = ""
    if request.method == "GET":
        return render_template("setting.html", user=current_user, notes=notes)
    if request.method == "POST":
        return render_template("setting.html", user=current_user, notes=notes)

@app.route('/login/youtube/authorize')
@login_required
def login_youtube_authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        app.instance_path + "beta_client_secret.json",
        scopes="https://www.googleapis.com/auth/youtube.force-ssl")
    flow.redirect_uri = url_for("login_youtube_oauth_callback", _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type="offline",
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes="true")

    # Store the state so the callback can verify the auth server response.
    session["state"] = state
    return redirect(authorization_url)

@app.route("/login/youtube/oauth_callback")
@login_required
def login_youtube_oauth_callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = session["state"]

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        app.instance_path + "beta_client_secret.json",
        scopes="https://www.googleapis.com/auth/youtube.force-ssl",
        state=state)
    flow.redirect_uri = url_for("login_youtube_oauth_callback", _external=True)
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

    # return redirect(url_for("login_setting"))
    return render_template("setting.html", user=current_user, notes=credentials_dict)

@app.route("/login/youtube/revoke")
@login_required
def login_youtube_revoke():
    if not current_user.youtube_credentials:
        return render_template("empty.html", content="Credentials not set")
    credentials = google.oauth2.credentials.Credentials(**current_user.youtube_credentials)
    response = requests.post("https://accounts.google.com/o/oauth2/revoke",
                             params={"token": credentials.token},
                             headers={"content-type": "application/x-www-form-urlencoded"})
    if response.status_code == 200:
        current_user.youtube_credentials = {}
    # return redirect(url_for("login_setting"))
    return render_template("setting.html", user=current_user, notes=[response.status_code, response.text])

#     #     #
#     #     # #    # #####
#     #     # #    # #    #
#     ####### #    # #####
#     #     # #    # #    #
#     #     # #    # #    #
#     #     #  ####  #####

@app.route("/hub/history")
def hub_history():
    """List all callback history of all channel"""
    callbacks = Callback.query.order_by(Callback.received_datetime.desc()).all()
    return render_template("hub_history.html", callbacks=callbacks)

@app.route("/hub/history/<channel_id>")
def hub_history_channel(channel_id):
    """List all callback history of a specific channel"""
    callbacks = Callback.query.filter_by(
        channel_id=channel_id).order_by(Callback.received_datetime.desc()).all()
    subscription = Subscription.query.filter(Subscription.channel_id == channel_id).first_or_404()
    return render_template("hub_history.html",
                           callbacks=callbacks,
                           channel_name=subscription.channel_name)

@app.route("/hub/status")
def hub_status():
    channels = Subscription.query.order_by(Subscription.channel_name).all()
    return render_template("status.html", channels=channels)

@app.route("/hub/status_api/<channel_id>/")
def hub_status_api_channel(channel_id):
    data = request_hub_status(channel_id, request.url_root + channel_id + "/callback")
    return data.text

@app.route("/hub/status_api_tmp/<channel_id>/")
def hub_status_api_tmp_channel(channel_id):
    data = request_hub_status(channel_id, request.url_root + channel_id + "/callback")
    return render_template("empty.html", content=data.__dict__)

@app.route("/hub/status/<channel_id>")
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

@app.route("/hub/renew-info/<channel_id>")
def hub_renew_info_channel(channel_id):
    subscription = Subscription.query.filter(Subscription.channel_id == channel_id).first_or_404()
    subscription.renew_info()
    return render_template("empty.html", content="Done")

@app.route("/hub/renew-info")
def hub_renew_info():
    for subscription in Subscription.query.filter(Subscription.active):
        subscription.renew_info()
    return render_template("empty.html", content="Done")

@app.route("/hub/renew/<channel_id>")
def hub_renew_channel(channel_id):
    subscription = Subscription.query.filter(Subscription.channel_id == channel_id).first_or_404()
    code = subscription.renew_hub().status_code
    return render_template("empty.html", content="Response HTTP Status Code: {status_code}".format(
        status_code=code))

@app.route("/hub/renew")
def hub_renew():
    response = {}
    for subscription in Subscription.query.filter(Subscription.active):
        response[subscription.channel_id] = subscription.renew_hub().status_code
    return render_template("empty.html", content=response)

#     ######
#     #     # #    #  ####  #    #  ####  #    # ###### #####
#     #     # #    # #      #    # #    # #    # #      #    #
#     ######  #    #  ####  ###### #    # #    # #####  #    #
#     #       #    #      # #    # #    # #    # #      #####
#     #       #    # #    # #    # #    #  #  #  #      #   #
#     #        ####   ####  #    #  ####    ##   ###### #    #

@app.route("/pushover/push", methods=["GET", "POST"])
@login_required
def pushover_push():
    if request.method == "GET":
        return render_template("pushover_push.html")
    elif request.method == "POST":
        form_datas = request.form
        response = send_notification("Test", current_user, form_datas["message"], title=form_datas["title"])
        return render_template("empty.html", content=response)
    response = "Something Went Wrong!!!!"
    return render_template("empty.html", content=response)

@app.route("/pushover/history")
def pushover_history():
    notifications = Notification.query.order_by(Notification.sent_datetime.desc()).all()
    # for notification in notifications:
    #     continue
    #     notification.response = type(notification.response)
    return render_template("pushover_history.html", notifications=notifications)

#     #     #               #######
#      #   #   ####  #    #    #    #    # #####  ######
#       # #   #    # #    #    #    #    # #    # #
#        #    #    # #    #    #    #    # #####  #####
#        #    #    # #    #    #    #    # #    # #
#        #    #    # #    #    #    #    # #    # #
#        #     ####   ####     #     ####  #####  ######

@app.route("/youtube/video")
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

@app.route("/youtube/subscription")
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

@app.route("/youtube/playlist_insert/<video_id>")
@login_required
def youtube_playlist_insert(video_id):
    return render_template("empty.html", content=current_user.insert_video_to_playlist(video_id))

#      #####
#     #     #  ####  #    # ###### #####  #    # #      ###### #####
#     #       #    # #    # #      #    # #    # #      #      #    #
#      #####  #      ###### #####  #    # #    # #      #####  #    #
#           # #      #    # #      #    # #    # #      #      #####
#     #     # #    # #    # #      #    # #    # #      #      #   #
#      #####   ####  #    # ###### #####   ####  ###### ###### #    #

@app.route("/scheduler/jobs")
def scheduler_jobs():
    jobs = scheduler.get_jobs().copy()
    for ind, val in enumerate(jobs):
        jobs[ind] = str(val)
    return render_template("empty.html", content=jobs)

def middle():
    # send_notification("test_interval", "test interval"+str(datetime.now()),
    #                   title="test title",
    #                   url="https://www.google.com",
    #                   url_title="Google")
    with open("/var/www/Tubee/scheduler_test", "a") as f:
        f.write(str(datetime.now())+"\n")

@app.route("/scheduler/add_job")
def scheduler_add_job():
    job_response = scheduler.add_job(
        id="test",
        func=middle,
        trigger="interval",
        # args=["test_interval", "test interval"+str(datetime.now())],
        # kwargs={
        #     "title": "test title",
        #     "url": "https://www.google.com",
        #     "url_title": "Google"
        # },
        seconds=10)
    return render_template("empty.html", content=job_response)

@app.route("/scheduler/pause_job")
def scheduler_pause_job():
    response = scheduler.get_job("test").pause()
    return render_template("empty.html", content=response)

#     ######
#     #     # ###### #####  #  ####
#     #     # #      #    # # #
#     ######  #####  #    # #  ####
#     #   #   #      #    # #      #
#     #    #  #      #    # # #    #
#     #     # ###### #####  #  ####

# @app.route("/redis/set/<key>/<value>")
# def redis_write(key, value):
#     response = redis_store.set(key, value)
#     return render_template("empty.html", content=response)
#
# @app.route("/redis/get/<key>")
# def redis_read(key):
#     response = redis_store.get(key)
#     return render_template("empty.html", content=response)

#     ######
#     #     #  ####  #    # ##### ######  ####
#     #     # #    # #    #   #   #      #
#     ######  #    # #    #   #   #####   ####
#     #   #   #    # #    #   #   #           #
#     #    #  #    # #    #   #   #      #    #
#     #     #  ####   ####    #   ######  ####

@app.route("/dashboard")
def dashboard():
    subscriptions = Subscription.query.order_by(Subscription.channel_name).all()
    return render_template("dashboard.html", subscriptions=subscriptions)

@app.route("/channel/<channel_id>")
def channel():
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
    # video_img     video_title         published_dt    callback_dt
    #               (msg_box: video_id)                 (msg_box: callback_cnt)
    #                                                   (float: callback / notification detail)
    # 
    # (dynamic loading)
    return render_template("empty.html")

@app.route("/subscribe", methods=["GET", "POST"])
@login_required
def channel_subscribe():
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
        subscription = Subscription.query.filter(Subscription.channel_id == channel_id).first()
        if not subscription:
            subscription = Subscription(channel_id)
            db.session.add(subscription)
            try:
                db.session.commit()
            except Exception as e:
                send_notification("SQL Error", current_user, str(datetime.now())+"\n"+str(e),
                                  title="Tubee encontered a SQL Error!!")
        
        # Schedule renew datetime
        # job_response = scheduler.add_job(
        #     id="renew_"+channel_id,
        #     func=renew_subscription,
        #     trigger="interval",
        #     args=[new_subscription],
        #     days=4)

        current_user.subscribe_to(subscription)
        response = {
            # "Renew Jobs": job_response,
            "HTTP Status Code": subscription.activate_response.status_code
        }
        return render_template("empty.html", content=response)

@app.route("/unsubscribe/<channel_id>", methods=["GET", "POST"])
def unsubscribe_channel(channel_id):
    """
    Page To Ubsubscribe
    (1) Request confirmation with GET request
    (2) Submit the form POST request
    """
    subscription = Subscription.query.filter(Subscription.channel_id == channel_id).first_or_404()
    if request.method == "GET":
        return render_template("unsubscribe.html", channel_name=subscription.channel_name)
    if request.method == "POST":
        response = subscription.deactivate()
        app.logger.info(response)
        return render_template("empty.html", content=response)

@app.route("/summary/<channel_id>")
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

@app.route("/<channel_id>/callback", methods=["GET", "POST"])
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
            app.logger.info("Already Pushed")
            return str("pass")
        elif old_update:
            app.logger.info("Old Video Update")
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

#     ######  ####### #     #
#     #     # #       #     #
#     #     # #       #     #
#     #     # #####   #     #
#     #     # #        #   #
#     #     # #         # #
#     ######  #######    #

@app.route("/dev_map")
@login_required
def dev_map():
    links = []
    for rule in app.url_map.iter_rules():
        query = {arg: "[{0}]".format(arg) for arg in rule.arguments}
        url = url_for(rule.endpoint, **query)
        links.append((url, rule.endpoint))
    links.sort(key=lambda x: x[0])
    return render_template("map.html", links=links)
    # return render_template("map.html", map=app.url_map.iter_rules())

@app.route("/dev_os")
@login_required
def dev_os_dict():
    target_dict = os.__dict__
    pprint_en = isinstance(target_dict, dict)
    if pprint_en:
        target_dict = pprint.pformat(target_dict)
    return render_template("empty.html", content=target_dict, pprint=pprint_en)

@app.route("/dev_sys")
@login_required
def dev_sys_dict():
    target_dict = sys.__dict__
    pprint_en = isinstance(target_dict, dict)
    if pprint_en:
        target_dict = pprint.pformat(target_dict)
    return render_template("empty.html", content=target_dict, pprint=pprint_en)

@app.route("/dev_flask")
@login_required
def dev_flask_dict():
    target_dict = app.__dict__
    target_dict["apscheduler"] = target_dict["apscheduler"].__dict__
    target_dict["apscheduler"]["_scheduler"] = target_dict["apscheduler"]["_scheduler"].__dict__
    pprint_en = isinstance(target_dict, dict)
    if pprint_en:
        target_dict = pprint.pformat(target_dict)
    return render_template("empty.html", content=target_dict, pprint=pprint_en)

@app.route("/dev_login-manager")
@login_required
def dev_login_manager_dict():
    target_dict = login_manager.__dict__
    pprint_en = isinstance(target_dict, dict)
    if pprint_en:
        target_dict = pprint.pformat(target_dict)
    return render_template("empty.html", content=target_dict, pprint=pprint_en)

@app.route("/dev_scheduler")
@login_required
def dev_scheduler_dict():
    target_dict = scheduler.__dict__
    target_dict["_scheduler"] = scheduler.scheduler.__dict__
    pprint_en = isinstance(target_dict, dict)
    if pprint_en:
        target_dict = pprint.pformat(target_dict)
    return render_template("empty.html", content=target_dict, pprint=pprint_en)

@app.route("/dev_user")
@login_required
def dev_user_dict():
    target_dict = current_user.__dict__
    pprint_en = isinstance(target_dict, dict)
    if pprint_en:
        target_dict = pprint.pformat(target_dict)
    return render_template("empty.html", content=target_dict, pprint=pprint_en)

@app.route("/instance")
@login_required
def dev_instance():
    instances_set = redis_store.smembers("INSTANCE_SET")
    instances_list = [instance.decode("utf-8") for instance in instances_set]
    response = "Instance ID: " + app.config["INSTANCE_ID"] + "\n" + \
                "Session ID: " + redis_store.get("SESSION_ID").decode("utf-8") + "\n" + \
                "Active Instances: " + "\n" + \
                pprint.pformat(instances_list)
    return render_template("empty.html", content=response, pprint=True)

@app.route("/dev_empty")
def dev_empty():
    return render_template("empty.html")

@app.route("/dev_broken")
def dev_broken():
    return something
