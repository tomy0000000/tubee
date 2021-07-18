from flask import Blueprint, abort, jsonify
from flask_login import current_user, login_required

from tubee.forms import TagSubscriptionForm

api_subscription_blueprint = Blueprint("api_subscription", __name__)


@api_subscription_blueprint.route("/untag", methods=["POST"])
@login_required
def untag():
    """Remove a tag from subscription"""
    form = TagSubscriptionForm(hidden_mode=True)
    if not form.validate_on_submit():
        abort(403)

    subscription = current_user.subscriptions.filter_by(
        channel_id=form.channel_id.data
    ).first_or_404()
    tag = current_user.tags.filter_by(name=form.tag_name.data).first_or_404()

    results = subscription.untag(tag.id)
    response = {"success": results}
    return jsonify(response)
