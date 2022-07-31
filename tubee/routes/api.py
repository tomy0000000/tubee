"""API for Frontend Access"""
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from tubee.exceptions import ServiceNotAuth

from ..utils import api_error_handler

api_blueprint = Blueprint("api", __name__)
api_blueprint.register_error_handler(Exception, api_error_handler)


@api_blueprint.route("/user/services")
@login_required
def user_services():
    status = {}
    for service in ["youtube", "pushover", "line_notify", "dropbox"]:
        try:
            status[service] = bool(getattr(current_user, service))
        except ServiceNotAuth:
            status[service] = False
    return jsonify(status)


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
    return jsonify(response)
