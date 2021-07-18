from flask import Blueprint, abort, jsonify
from flask.helpers import url_for
from flask_login import current_user, login_required

from ..forms import TagForm, TagRenameForm, TagSubscriptionForm
from ..models import Tag

api_tag_blueprint = Blueprint("api_tag", __name__)


@api_tag_blueprint.route("/new", methods=["POST"])
@login_required
def new():
    form = TagSubscriptionForm()
    if not form.validate_on_submit():
        abort(403)
    subscription = current_user.subscriptions.filter_by(
        channel_id=form.channel_id.data
    ).first_or_404()
    response = subscription.tag(form.tag_name.data)
    return jsonify(str(response))


@api_tag_blueprint.route("/rename", methods=["POST"])
@login_required
def rename():
    form = TagRenameForm()
    if not form.validate_on_submit():
        abort(403)
    tag = Tag.query.filter_by(name=form.tag_name.data).first_or_404()
    response = {
        "success": tag.rename(form.new_tag_name.data),
        "redirect": url_for("main.dashboard", tag_name=form.new_tag_name.data),
    }
    return jsonify(response)


@api_tag_blueprint.route("/remove", methods=["POST"])
@login_required
def remove():
    form = TagForm(hidden_mode=True)
    if not form.validate_on_submit():
        abort(403)
    tag = current_user.tags.filter_by(name=form.tag_name.data).first_or_404()
    response = {
        "success": tag.delete(),
        "redirect": url_for("main.dashboard", tag_name=False),
    }
    return jsonify(response)
