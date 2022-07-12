from flask import Blueprint, abort, jsonify, request
from flask_login import current_user, login_required

from ..models import Video
from ..utils import admin_required_decorator as admin_required

api_video_blueprint = Blueprint("api_video", __name__)


@api_video_blueprint.route("/<video_id>/update_infos")
@login_required
@admin_required
def update_infos(video_id):
    video = Video.query.get_or_404(video_id)
    response = video.update_infos()
    return jsonify(response)


@api_video_blueprint.route("/<video_id>/execute/<action_id>")
@login_required
def execute_action(video_id, action_id):
    video = Video.query.get_or_404(video_id, "Video not found")
    response = video.execute_action(action_id)
    return jsonify(response)


@api_video_blueprint.route("/mark_as_checked")
@login_required
def mark_as_checked():
    video_ids = request.args.get("video_ids")
    if not video_ids:
        abort(404)
    video_ids = video_ids.split(",")
    response = [current_user.mark_video_as_checked(video_id) for video_id in video_ids]
    return jsonify(response)
