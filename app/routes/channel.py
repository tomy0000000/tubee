"""Channel Related Routes"""
import bs4
import json
from apiclient.errors import HttpError
from datetime import datetime
from dateutil import parser
from flask import Blueprint, current_app, render_template, request
from flask_login import current_user, login_required
from .. import db
from ..helper import send_notification
from ..models import Callback, Request, Subscription, User
channel = Blueprint("channel", __name__)

@channel.route("/<channel_id>")
def channel_page(channel_id):
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

    # TODO: Support New Un-Subscribed Channel
    subscription = Subscription.query.filter_by(channel_id=channel_id).first_or_404()
    return render_template("channel.html", subscription=subscription)

# TODO: REBUILD THIS DAMN MESSY ROUTE
@channel.route("/subscribe", methods=["GET", "POST"])
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
        return render_template("empty.html", info=response)

# TODO: REBUILD THIS DAMN MESSY ROUTE
@channel.route("/unsubscribe/<channel_id>", methods=["GET", "POST"])
@login_required
def unsubscribe(channel_id):
    """
    Page To Ubsubscribe
    (1) Request confirmation with GET request
    (2) Submit the form POST request
    """
    subscription = Subscription.query.filter_by(channel_id=channel_id).first_or_404()
    if request.method == "GET":
        response_page = render_template("unsubscribe.html", channel_name=subscription.channel_name)
    elif request.method == "POST":
        response = subscription.deactivate()
        current_app.logger.info(response)
        response_page = render_template("empty.html", info=response)
    return response_page


# TODO: REBUILD THIS DAMN MESSY ROUTE
@channel.route("/<channel_id>/callback", methods=["GET", "POST"])
def callback(channel_id):
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
        response = Tomy.send_notification("Callback", message,
                                          title=title,
                                          url="https://www.youtube.com/watch?v="+video_id,
                                          url_title=soup.entry.find("title").string,
                                          image=image_url)

    return str(response)
