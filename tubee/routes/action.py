from flask import Blueprint, render_template
from flask_login import current_user, login_required

from ..forms import ActionForm
from ..models import Action

action_blueprint = Blueprint("action", __name__)


@action_blueprint.get("/")
def listing():
    actions = current_user.actions.all()
    return render_template("action/main.html", actions=actions)


@action_blueprint.get("/form")
@login_required
def form_empty():
    form = ActionForm()
    return render_template("action/form.html", form=form)


@action_blueprint.get("/form/<action_id>")
@login_required
def form_read(action_id: int):
    action = Action.query.filter_by(
        id=action_id, username=current_user.username
    ).first_or_404()
    form = ActionForm()
    return render_template("action/form.html", form=form, action=action)
