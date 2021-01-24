from flask import Blueprint, abort, jsonify
from flask_login import current_user, login_required

from ..forms import TagForm

api_tag_blueprint = Blueprint("api_tag", __name__)


@api_tag_blueprint.route("/new", methods=["POST"])
@login_required
def new():
    form = TagForm()
    if form.validate_on_submit():
        subscription = current_user.subscriptions.filter_by(
            channel_id=form.channel_id.data
        ).first_or_404()
        response = subscription.add_tag(form.tag_name.data)
        return jsonify(str(response))
    abort(403)
