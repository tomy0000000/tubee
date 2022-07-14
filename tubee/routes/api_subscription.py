from flask import Blueprint, abort, jsonify, request
from flask_login import current_user, login_required

from tubee.forms import SubscriptionTagForm

api_subscription_blueprint = Blueprint("api_subscription", __name__)


@api_subscription_blueprint.post("/")
@login_required
def create():
    """Add Subscription"""
    channel_id = request.get_json().get("channel_id")
    return jsonify(current_user.subscribe(channel_id))


@api_subscription_blueprint.delete("/")
@login_required
def delete():
    """Remove subscription"""
    channel_id = request.get_json().get("channel_id")
    return jsonify(current_user.unbsubscribe(channel_id))


@api_subscription_blueprint.post("/tag")
@login_required
def tag():
    """Add a tag to subscription"""
    form = SubscriptionTagForm()
    if not form.validate_on_submit():
        abort(403)
    subscription = current_user.subscriptions.filter_by(
        channel_id=form.channel_id.data
    ).first_or_404()
    response = subscription.tag(form.tag_name.data)
    return jsonify(str(response))


@api_subscription_blueprint.route("/untag", methods=["POST"])
@login_required
def untag():
    """Remove a tag from subscription"""
    form = SubscriptionTagForm(tag_name_hidden=True)
    if not form.validate_on_submit():
        abort(403)

    subscription = current_user.subscriptions.filter_by(
        channel_id=form.channel_id.data
    ).first_or_404()
    tag = current_user.tags.filter_by(name=form.tag_name.data).first_or_404()

    results = subscription.untag(tag.id)
    response = {"success": results}
    return jsonify(response)
