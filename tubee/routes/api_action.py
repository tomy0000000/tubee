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
        abort(400)
    return jsonify(str(Action(current_user.username, form.data)))


@api_action_blueprint.route("/<action_id>")
@login_required
def action(action_id):
    """Get JSON of subscription action"""
    action = Action.query.filter_by(
        id=action_id, username=current_user.username
    ).first_or_404()
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
    action = Action.query.filter_by(
        id=action_id, username=current_user.username
    ).first_or_404()
    return jsonify(action.delete())


@api_action_blueprint.route("/<action_id>", methods=["PATCH"])
@login_required
def edit(action_id):
    action = Action.query.filter_by(
        id=action_id, username=current_user.username
    ).first_or_404()
    form = ActionForm()
    if not form.validate_on_submit():
        abort(400)
    return jsonify(action.edit(form.data))
