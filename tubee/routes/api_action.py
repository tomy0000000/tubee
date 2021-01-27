from flask import Blueprint, abort, jsonify
from flask_login import current_user, login_required

from ..forms import ActionForm
from ..models import Action

api_action_blueprint = Blueprint("api_action", __name__)


@api_action_blueprint.route("/new", methods=["POST"])
@login_required
def new():
    form = ActionForm()
    if not form.validate_on_submit():
        abort(403)

    if form.action_type.data == "Notification":
        details = form.notification.data
    elif form.action_type.data == "Playlist":
        details = form.playlist.data
    elif form.action_type.data == "Download":
        details = form.download.data

    if form.channel_id.data:
        action_mixin = current_user.subscriptions.filter_by(
            channel_id=form.channel_id.data
        ).first_or_404()
    elif form.tag.data:
        action_mixin = current_user.tags.filter_by(name=form.tag.data).first_or_404()
    else:
        abort(403)

    response = action_mixin.add_action(
        form.action_name.data, form.action_type.data, details
    )
    return jsonify(str(response))


@api_action_blueprint.route("/<action_id>")
@login_required
def action(action_id):
    """Get JSON of subscription action"""
    action = Action.query.filter_by(id=action_id).first_or_404()
    if action.subscription:
        if action.subscription not in current_user.subscriptions:
            abort(403)
    elif action.tag:
        if action.tag not in current_user.tags:
            abort(403)
    else:
        abort(403)
    return jsonify(
        dict(
            action_id=action.id,
            action_name=action.name,
            action_type=action.type.value,
            details=action.details,
        )
    )


@api_action_blueprint.route("/<action_id>", methods=["DELETE"])
@login_required
def delete(action_id):
    action = Action.query.filter_by(id=action_id).first_or_404()
    if action.subscription:
        if action.subscription not in current_user.subscriptions:
            abort(403)
    elif action.tag:
        if action.tag not in current_user.tags:
            abort(403)
    else:
        abort(403)
    return jsonify(action.action_mixin.remove_action(action_id))


@api_action_blueprint.route("/<action_id>", methods=["PATCH"])
@login_required
def edit(action_id):
    action = Action.query.filter_by(id=action_id).first_or_404()
    if action.subscription:
        if action.subscription not in current_user.subscriptions:
            abort(403)
    elif action.tag:
        if action.tag not in current_user.tags:
            abort(403)
    else:
        abort(403)
    form = ActionForm()
    if not form.validate_on_submit():
        abort(403)

    modified = action.edit(form.data)
    return jsonify(modified)
