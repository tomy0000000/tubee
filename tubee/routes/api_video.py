from flask import Blueprint, jsonify
from flask_login import login_required

from ..helper import admin_required_decorator as admin_required
from ..models import Video

api_video_blueprint = Blueprint("api_video", __name__)


@api_video_blueprint.route("/<video_id>/update_infos")
@login_required
@admin_required
def update_infos(video_id):
    video = Video.query.get_or_404(video_id)
    response = video.update_infos()
    return jsonify(response)
