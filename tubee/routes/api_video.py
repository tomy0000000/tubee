from datetime import datetime, timedelta

from flask import Blueprint, abort, get_template_attribute, jsonify, request
from flask_login import current_user, login_required

from .. import db
from ..models import Channel, Subscription, Video, VideoCheck
from ..utils import admin_required_decorator as admin_required

api_video_blueprint = Blueprint("api_video", __name__)


@api_video_blueprint.get("/<video_id>/update_infos")
@login_required
@admin_required
def update_infos(video_id):
    video = Video.query.get_or_404(video_id)
    response = video.update_infos()
    return jsonify(response)


@api_video_blueprint.get("/<video_id>/execute/<action_id>")
@login_required
def execute_action(video_id, action_id):
    video = Video.query.get_or_404(video_id, "Video not found")
    response = video.execute_action(action_id)
    return jsonify(response)


@api_video_blueprint.get("/mark_as_checked")
@login_required
def mark_as_checked():
    video_ids = request.args.get("video_ids")
    if not video_ids:
        abort(404)
    video_ids = video_ids.split(",")
    response = [current_user.mark_video_as_checked(video_id) for video_id in video_ids]
    return jsonify(response)


@api_video_blueprint.get("unchecked")
@login_required
def unchecked():
    draw = int(request.args.get("draw"))
    start = int(request.args.get("start"))
    length = int(request.args.get("length"))
    order_column = int(request.args.get("order[0][column]"))
    order_dir = request.args.get("order[0][dir]")

    ORDER_MAP = {
        (1, "asc"): Channel.name.asc(),
        (1, "desc"): Channel.name.desc(),
        (2, "asc"): Video.name.asc(),
        (2, "desc"): Video.name.desc(),
        (3, "asc"): Video.uploaded_timestamp.asc(),
        (3, "desc"): Video.uploaded_timestamp.desc(),
    }

    last_30_days = datetime.utcnow() - timedelta(days=30)
    query = (
        db.session.query(Subscription, Channel, Video, VideoCheck)
        .outerjoin(Channel, Subscription.channel_id == Channel.id)
        .outerjoin(Video, Subscription.channel_id == Video.channel_id)
        .outerjoin(VideoCheck, VideoCheck.video_id == Video.id)
        .where(Subscription.username == current_user.username)
        .where(Video.uploaded_timestamp > last_30_days)
        .where(VideoCheck.checked.is_(None) | VideoCheck.checked.is_(False))
        .order_by(ORDER_MAP[(order_column, order_dir)])
    )
    count = query.count()
    rows = query.slice(start, start + length).all()

    response = {
        "datatable": True,
        "draw": draw,
        "recordsTotal": count,
        "recordsFiltered": count,
        "data": [
            [
                get_template_attribute("macros/video.html", "table_thumbnails")(row),
                get_template_attribute("macros/video.html", "table_channel")(row),
                get_template_attribute("macros/video.html", "table_title")(row),
                get_template_attribute("macros/video.html", "table_published")(row),
                get_template_attribute("macros/video.html", "table_actions")(row),
                row["Video"].id,
            ]
            for row in rows
        ],
    }
    return response
