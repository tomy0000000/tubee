"""API for Frontend Access"""
from flask import Blueprint, request
from flask_login import current_user, login_required

from tubee.exceptions import ServiceNotAuth

api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/user/services")
@login_required
def user_services():
    response = {}
    for service in ["youtube", "pushover", "line_notify", "dropbox"]:
        try:
            response[service] = bool(getattr(current_user, service))
        except ServiceNotAuth:
            response[service] = False
    return response


@api_blueprint.route("/youtube/subscription")
@login_required
def youtube_subscription():
    """For Dynamically Loading User's YouTube Subscription"""
    page_token = request.args.get("page_token")
    response = (
        current_user.youtube.subscriptions()
        .list(
            part="snippet",
            maxResults=50,
            mine=True,
            order="alphabetical",
            pageToken=page_token,
        )
        .execute()
    )
    for channel in response["items"]:
        channel_id = channel["snippet"]["resourceId"]["channelId"]
        channel["snippet"]["subscribed"] = current_user.is_subscribing(channel_id)
    return response
