from flask import Blueprint, abort, jsonify, request
from flask_login import current_user  # type: ignore
from flask_login import login_required

from ..models import Tag, User

current_user: User

api_tag_blueprint = Blueprint("api_tag", __name__)


@api_tag_blueprint.patch("/")
@login_required
def update_sort_indexes():
    """Update sort index"""
    if not (data := request.get_json()):
        abort(400, "No order provided")
    order = data.get("order")
    tags = current_user.tags.all()
    results = []
    for tag in tags:
        new_index = order.index(tag.id) if tag.id in order else None
        results.append(tag.set_sort_index(new_index))
    return jsonify(results)


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
