"""The Main Routes"""
from datetime import datetime
from flask import Blueprint, current_app, render_template, request
from flask_login import current_user, login_required
from .. import db
from ..models import Subscription
main = Blueprint("main", __name__)

@main.context_processor
def inject_username():
    if current_user.is_anonymous:
        username = "Guest"
    else:
        username = current_user.username
    return dict(username=username)

@main.route("/")
@login_required
def dashboard(alert="", alert_type=""):
    """Showing All Subscribed Channels"""
    subscriptions = Subscription.query.order_by(Subscription.channel_name).all()
    return render_template("dashboard.html",
                           subscriptions=subscriptions,
                           alert=alert,
                           alert_type=alert_type)

@main.route("/channel/<channel_id>")
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

@main.route("/subscribe", methods=["GET", "POST"])
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

@main.route("/unsubscribe/<channel_id>", methods=["GET", "POST"])
@login_required
def unsubscribe_channel(channel_id):
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
