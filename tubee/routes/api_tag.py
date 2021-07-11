from flask import Blueprint, abort, jsonify
from flask.helpers import url_for
from flask_login import current_user, login_required

from ..forms import TagForm, TagRenameForm
from ..models import Tag

api_tag_blueprint = Blueprint("api_tag", __name__)


@api_tag_blueprint.route("/new", methods=["POST"])
@login_required
def new():
    form = TagForm()
    if not form.validate_on_submit():
        abort(403)
    subscription = current_user.subscriptions.filter_by(
        channel_id=form.channel_id.data
    ).first_or_404()
    response = subscription.add_tag(form.tag_name.data)
    return jsonify(str(response))


@api_tag_blueprint.route("/rename", methods=["POST"])
@login_required
def rename():
    form = TagRenameForm()
    if not form.validate_on_submit():
        abort(403)
    tag = Tag.query.filter_by(name=form.tag_name.data).first_or_404()
    tag.rename(form.new_tag_name.data)
    results = {
        "success": True,
        "redirect": url_for("main.dashboard", tag=form.new_tag_name.data),
    }
    return jsonify(results)
