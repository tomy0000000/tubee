"""The Main Routes"""
from flask import Blueprint, render_template, session, url_for
from flask_login import current_user, login_required
from ..helper.youtube import build_service
from ..models.channel import Channel
from ..models.user_subscription import UserSubscription
main_blueprint = Blueprint("main", __name__)

@main_blueprint.route("/")
@login_required
def dashboard():
    """Showing All Subscribed Channels"""
    alert = session.pop("alert", None)
    alert_type = session.pop("alert_type", None)
    subscriptions = current_user.subscriptions.join(
        UserSubscription.channel).order_by(
            Channel.channel_name.asc()
        ).all()
    return render_template("dashboard.html",
                           subscriptions=subscriptions,
                           alert=alert,
                           alert_type=alert_type)

@main_blueprint.route("/tmp")
def tmp():
    subscriptions = current_user.subscriptions
    return render_template("empty.html", info=subscriptions)

@main_blueprint.route("/explore")
def explore():
    """Page to Explore New Channels"""
    return render_template("explore.html")

@main_blueprint.route("/youtube/subscription")
@login_required
def youtube_subscription():
    """Showing User's YouTube Subsciptions"""
    youtube_service = build_service(current_user.youtube_credentials)
    response = youtube_service.subscriptions().list(
        part="snippet",
        maxResults=50,
        mine=True,
        order="alphabetical"
    ).execute()
    for channel in response["items"]:
        channel_id = channel["snippet"]["resourceId"]["channelId"]
        channel["snippet"]["subscribed"] = current_user.is_subscribing(channel_id)
        channel["snippet"]["subscribe_endpoint"] = url_for("api.channel_subscribe", channel_id=channel_id)
    return render_template("youtube_subscription.html", response=response)
