from flask import Blueprint, abort, jsonify, request, url_for
from flask_login import current_user, login_required

from ..forms import TagForm
from ..models import Tag

api_tag_blueprint = Blueprint("api_tag", __name__)


@api_tag_blueprint.patch("/<tag_id>")
@login_required
def update(tag_id):
    """Update Tag"""
    tag = Tag.query.get_or_404(tag_id)
    if tag.username != current_user.username:
        abort(403)
    result = tag.rename(request.get_json().get("name"))
    return jsonify(result)


@api_tag_blueprint.route("/remove", methods=["POST"])
@login_required
def remove():
    form = TagForm(tag_name_hidden=True)
    if not form.validate_on_submit():
        abort(403)
    tag = current_user.tags.filter_by(name=form.tag_name.data).first_or_404()
    response = {
        "success": tag.delete(),
        "redirect": url_for("main.dashboard", tag_id=False),
    }
    return jsonify(response)
