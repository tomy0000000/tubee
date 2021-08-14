from flask import Blueprint, abort, jsonify
from flask_login import current_user, login_required

from tubee.forms import SubscriptionForm, SubscriptionTagForm

api_subscription_blueprint = Blueprint("api_subscription", __name__)


@api_subscription_blueprint.route("/add", methods=["POST"])
@login_required
def add():
    """Add a new subscription"""
    form = SubscriptionForm()
    if not form.validate_on_submit():
        abort(403)

    results = current_user.subscribe_to(form.channel_id.data)
    response = {"success": results}
    return jsonify(response)


@api_subscription_blueprint.route("/remove", methods=["POST"])
@login_required
def remove():
    """Remove a new subscription"""
    form = SubscriptionForm(channel_id_hidden=True)
    if not form.validate_on_submit():
        abort(403)

    results = current_user.unbsubscribe(form.channel_id.data)
    response = {"success": results}
    return jsonify(response)


@api_subscription_blueprint.route("/tag", methods=["POST"])
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
