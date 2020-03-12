"""The Main Routes"""
from flask import Blueprint, current_app, render_template, url_for
from flask_login import current_user, login_required
from ..helper import youtube_required
from ..models import Channel, Subscription
main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
@login_required
def dashboard():
    """Showing All Subscribed Channels"""
    subscriptions = current_user.subscriptions.join(
        Subscription.channel).order_by(Channel.name.asc()).all()
    return render_template("dashboard.html",
                           subscriptions=subscriptions)


@main_blueprint.route("/youtube/subscription")
@login_required
@youtube_required
def youtube_subscription():
    """Showing User's YouTube Subsciptions"""
    response = current_user.youtube.subscriptions().list(
        part="snippet", maxResults=50, mine=True,
        order="alphabetical").execute()
    for channel in response["items"]:
        channel_id = channel["snippet"]["resourceId"]["channelId"]
        channel["snippet"]["subscribed"] = current_user.is_subscribing(
            channel_id)
        channel["snippet"]["subscribe_endpoint"] = url_for(
            "api.channel_subscribe", channel_id=channel_id)
    return render_template("youtube_subscription.html", response=response)


@main_blueprint.route("/raise-error")
def raise_error():
    raise RuntimeError("Test RuntimeError")


@main_blueprint.route("/write-logs")
def write_logs():
    current_app.logger.debug("debug Log")
    current_app.logger.info("info Log")
    current_app.logger.warning("warning Log")
    current_app.logger.error("error Log")
    current_app.logger.critical("critical Log")
    return render_template("empty.html")
