from flask import Blueprint, abort, jsonify, request
from flask_login import current_user, login_required

from ..models import Tag

api_tag_blueprint = Blueprint("api_tag", __name__)


@api_tag_blueprint.patch("/<tag_id>")
@login_required
def update(tag_id):
    """Update Tag"""
    tag = Tag.query.get_or_404(tag_id)
    if tag.username != current_user.username:
        abort(403)
    response = tag.rename(request.get_json().get("name"))
    return jsonify(response)


@api_tag_blueprint.delete("/<tag_id>")
@login_required
def delete(tag_id):
    tag = current_user.tags.filter_by(id=tag_id).first_or_404()
    response = tag.delete()
    return jsonify(response)
