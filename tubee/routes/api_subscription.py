from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

api_subscription_blueprint = Blueprint("api_subscription", __name__)


@api_subscription_blueprint.post("/")
@login_required
def create():
    """Add Subscription"""
    channel_id = request.get_json().get("channel_id")
    response = current_user.subscribe(channel_id)
    return jsonify(response)


@api_subscription_blueprint.delete("/")
@login_required
def delete():
    """Remove subscription"""
    channel_id = request.get_json().get("channel_id")
    response = current_user.unbsubscribe(channel_id)
    return jsonify(response)


@api_subscription_blueprint.post("/tag")
@login_required
def tag_create():
    """Add a tag to subscription"""
    data = request.get_json()
    channel_id = data.get("channel_id")
    tag_name = data.get("tag_name")

    subscription = current_user.subscriptions.filter_by(
        channel_id=channel_id
    ).first_or_404()
    response = subscription.tag(tag_name)
    return jsonify(response)


@api_subscription_blueprint.delete("/tag")
@login_required
def tag_delete():
    """Remove a tag from subscription"""
    data = request.get_json()
    channel_id = data.get("channel_id")
    tag_id = data.get("tag_id")

    subscription = current_user.subscriptions.filter_by(
        channel_id=channel_id
    ).first_or_404("Channel not found")
    response = subscription.untag(tag_id)
    return jsonify(response)
