from flask import Blueprint, abort, jsonify
from flask_login import current_user, login_required  # type: ignore

from ..forms import ActionForm
from ..models import Action, User

current_user: User

api_action_blueprint = Blueprint("api_action", __name__)


@api_action_blueprint.post("/")
@login_required
def create():
    form = ActionForm()
    if not form.validate_on_submit():
        abort(400)
    response = Action(current_user.username, form.data)
    return jsonify(response)


@api_action_blueprint.get("/<action_id>")
@login_required
def read(action_id):
    """Get JSON of subscription action"""
    action = Action.query.filter_by(
        id=action_id, username=current_user.username
    ).first_or_404()
    return jsonify(action)


@api_action_blueprint.patch("/<action_id>")
@login_required
def update(action_id):
    action = Action.query.filter_by(
        id=action_id, username=current_user.username
    ).first_or_404()
    form = ActionForm()
    if not form.validate_on_submit():
        abort(400)
    response = action.edit(form.data)
    return response


@api_action_blueprint.delete("/<action_id>")
@login_required
def delete(action_id):
    action = Action.query.filter_by(
        id=action_id, username=current_user.username
    ).first_or_404()
    response = action.delete()
    return jsonify(response)
