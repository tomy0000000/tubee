from flask import Blueprint, abort, jsonify
from flask.helpers import url_for
from flask_login import current_user, login_required

from ..forms import TagForm, TagRenameForm
from ..models import Tag

api_tag_blueprint = Blueprint("api_tag", __name__)


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
    form = TagForm(tag_name_hidden=True)
    if not form.validate_on_submit():
        abort(403)
    tag = current_user.tags.filter_by(name=form.tag_name.data).first_or_404()
    response = {
        "success": tag.delete(),
        "redirect": url_for("main.dashboard", tag_name=False),
    }
    return jsonify(response)
