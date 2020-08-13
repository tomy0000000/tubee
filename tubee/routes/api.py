"""API for Frontend Access"""
import logging
from datetime import datetime, timedelta

# from celery.result import AsyncResult
from flask import Blueprint, abort, current_app, jsonify, request, url_for
from flask_login import current_user, login_required
from flask_migrate import Migrate, upgrade

# from google.cloud.tasks_v2.types import Task as GoogleCloudTask

from ..forms import ActionForm
from ..helper import (
    app_engine_required,
    build_callback_url,
    build_topic_url,
    notify_admin,
)
from ..models import Action, Channel
from ..tasks import renew_channels

api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/deploy")
def deploy():
    """Run deployment tasks."""

    # Verify Key
    server_key = current_app.config["DEPLOY_KEY"]
    client_key = request.args.to_dict().get("key")
    if not server_key:
        logging.info("Deploy triggered without server key")
    if not client_key:
        logging.info("Deploy triggered without client key")
    if server_key != client_key:
        logging.info("Deploy triggered but keys don't matched")
    if not server_key or not client_key or server_key != client_key:
        abort(401)

    # Run tasks, notify admins if anything went wrong
    try:
        # migrate database to latest revision
        migrate = Migrate(current_app, current_app.db, render_as_batch=True)
        upgrade()
        response = "Deployment Task Completed"
    except Exception as error:
        response = notify_admin(
            "Deployment", "Pushover", message=error, title="Deployment Error"
        )
    return jsonify(response)


@api_blueprint.route("/task/<task_id>/status")
@login_required
def task_status(task_id):
    task = renew_channels.AsyncResult(task_id)
    response = {
        "id": task.id,
        "status": task.status.title(),
        "current": task.result.get("current", 1),
        "total": task.result.get("total", 1),
        "channel_id": task.result.get("channel_id", None),
        "result": task.result,
        "traceback": task.traceback,
    }
    return jsonify(response)


@api_blueprint.route("/user/services")
@login_required
def user_info():
    status = {}
    for service in ["youtube", "pushover", "line_notify", "dropbox"]:
        status[service] = bool(getattr(current_user, service))
    return jsonify(status)


@api_blueprint.route("/channels/cron-renew")
@app_engine_required
def channels_cron_renew():
    channel_ids_with_url = []
    for channel in Channel.query.all():
        if channel.hub_infos["state"] != "verified" or (
            channel.expiration
            and channel.expiration < datetime.now() + timedelta(days=2)
        ):
            channel_ids_with_url.append(
                (
                    channel.id,
                    build_callback_url(channel.id),
                    build_topic_url(channel.id),
                )
            )
    # task = schedule_channels_renew(channels)
    task = renew_channels.apply_async(args=[channel_ids_with_url])
    logging.info("Cron Renew Triggered: {task.id}")
    notify_admin(
        "Cron Renew", "Pushover", message=task.id, title="Cron Renew Triggered"
    )
    return jsonify(task.id)


@api_blueprint.route("/channels/renew")
@login_required
def channels_renew():
    """Renew Subscription Info, Both Hub and Info"""
    channel_ids_with_url = [
        (channel.id, build_callback_url(channel.id), build_topic_url(channel.id),)
        for channel in Channel.query.all()
    ]
    # task = schedule_channels_renew(Channel.query.all())
    task = renew_channels.apply_async(args=[channel_ids_with_url])
    response = None
    # if isinstance(task, GoogleCloudTask):
    #     response = {"name": task.name}
    # if isinstance(task, AsyncResult):
    response = {
        "id": task.id,
        "status": url_for("api.task_status", task_id=task.id),
    }
    return jsonify(response)


@api_blueprint.route("/<channel_id>/status")
def channel_status(channel_id):
    """From Hub fetch Status"""
    channel = Channel.query.filter_by(id=channel_id).first_or_404()
    response = channel.update_hub_infos()
    return jsonify(response)


@api_blueprint.route("/<channel_id>/subscribe")
@login_required
def channel_subscribe(channel_id):
    """Subscribe to a Channel"""
    return jsonify(current_user.subscribe_to(channel_id))


@api_blueprint.route("/<channel_id>/unsubscribe")
@login_required
def channel_unsubscribe(channel_id):
    """Unsubscribe to a Channel"""
    return jsonify(current_user.unbsubscribe(channel_id))


@api_blueprint.route("/<channel_id>/renew")
@login_required
def channel_renew(channel_id):
    """Renew Subscription Info, Both Hub and Info"""
    channel = Channel.query.filter_by(id=channel_id).first_or_404()
    response = channel.renew(stringify=True)
    return jsonify(response)


@api_blueprint.route("/<channel_id>/fetch-videos")
@login_required
def fetch_videos(channel_id):
    channel_item = Channel.query.filter_by(id=channel_id).first_or_404()
    response = channel_item.fetch_videos()
    return jsonify(response)


@api_blueprint.route("/<action_id>")
@login_required
def action(action_id):
    """Get JSON of subscription action"""
    action = Action.query.filter_by(id=action_id).first_or_404()
    if action.subscription not in current_user.subscriptions:
        abort(403)
    return jsonify(
        dict(
            action_id=action.id,
            action_name=action.name,
            action_type=action.type.value,
            details=action.details,
        )
    )


@api_blueprint.route("/action/new", methods=["POST"])
@login_required
def action_new():
    form = ActionForm()
    if form.validate_on_submit():
        subscription = current_user.subscriptions.filter_by(
            channel_id=form.channel_id.data
        ).first_or_404()
        if form.action_type.data == "Notification":
            details = {
                "service": "Pushover",
                "message": "{video_title}",
                "title": "New from {channel_name}",
                "url": "https://www.youtube.com/watch?v={video_id}",
                "url_title": "{video_title}",
                "image_url": "{video_thumbnails}",
            }
        elif form.action_type.data == "Playlist":
            details = {"playlist_id": "WL"}
        elif form.action_type.data == "Download":
            details = {"file_path": "/{video_title}.mp4"}
        response = subscription.add_action(
            form.action_name.data, form.action_type.data, details
        )
        return jsonify(str(response))
    abort(403)


@api_blueprint.route("/<action_id>/edit", methods=["POST"])
@login_required
def action_edit(action_id):
    # TODO
    action = Action.query.filter_by(id=action_id).first_or_404()
    if action.subscription not in current_user.subscriptions:
        abort(403)
    form = ActionForm()
    if form.validate_on_submit():
        subscription = current_user.subscriptions.filter_by(
            channel_id=form.channel_id.data
        ).first_or_404()
    return jsonify({})


@api_blueprint.route("/<action_id>/remove")
@login_required
def action_remove(action_id):
    action = Action.query.filter_by(id=action_id).first_or_404()
    if action.subscription not in current_user.subscriptions:
        abort(403)
    return str(action.subscription.remove_action(action_id))


@api_blueprint.route("/youtube/subscription")
@login_required
def youtube_subscription():
    """For Dynamically Loading User's YouTube Subscription"""
    page_token = request.args.get("page_token")
    response = (
        current_user.youtube.subscriptions()
        .list(
            part="snippet",
            maxResults=50,
            mine=True,
            order="alphabetical",
            pageToken=page_token,
        )
        .execute()
    )
    for channel in response["items"]:
        channel_id = channel["snippet"]["resourceId"]["channelId"]
        channel["snippet"]["subscribed"] = current_user.is_subscribing(channel_id)
        channel["snippet"]["subscribe_endpoint"] = url_for(
            "api.channel_subscribe", channel_id=channel_id
        )
    return jsonify(response)
