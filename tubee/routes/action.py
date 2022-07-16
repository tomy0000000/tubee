from flask import Blueprint, render_template
from flask_login import current_user, login_required

from ..forms import ActionForm
from ..models import Action

action_blueprint = Blueprint("action", __name__)


@action_blueprint.get("/")
@login_required
def empty():
    form = ActionForm()
    return render_template("action/form.html", form=form)


@action_blueprint.get("/<action_id>")
@login_required
def read(action_id: int):
    action = Action.query.filter_by(
        id=action_id, username=current_user.username
    ).first_or_404()
    form = ActionForm()
    return render_template("action/form.html", form=form, action=action)
