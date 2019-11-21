"""API for Frontend Access"""
from datetime import datetime
from flask import abort, Blueprint, current_app, jsonify, request, url_for
from flask_login import current_user, login_required
from flask_migrate import Migrate, upgrade
from .. import helper
from ..models import Channel
api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/deploy")
def deploy():
    """Run deployment tasks."""

    # Verify Key
    server_key = current_app.config["DEPLOY_KEY"]
    client_key = request.args.to_dict()["key"] if "key" in request.args.to_dict() else None
    if not server_key or not client_key or server_key != client_key:
        abort(401)

    # Run tasks, notify admins if anything went wrong
    try:
        # migrate database to latest revision
        migrate = Migrate(current_app, current_app.db, render_as_batch=True)
        upgrade()
        response = "Deployment Task Completed"
    except Exception as error:
        response = helper.notify_admin("Deployment",
                                       message=error,
                                       title="Deployment Error")
    return jsonify(response)


@api_blueprint.route("/test_cron_job")
def test_cron():
    if not request.headers.get("X-Appengine-Cron"):
        current_app.logger.info("Forbidden Triggered at {}".format(
            datetime.now()))
        abort(401)
    response = helper.notify_admin("test_cron_job",
                                   message=datetime.now(),
                                   title="Test Cron Job Triggered",
                                   priority=-2)
    current_app.logger.info("Test Cron Job Triggered at {}".format(
        datetime.now()))
    return jsonify(response)


@api_blueprint.route("/channels/renew")
@login_required
def channels_renew():
    """Renew Subscription Info, Both Hub and Info"""
    channels = Channel.query.all()
    response = {}
    for channel in channels:
        response[channel.channel_id] = channel.renew(stringify=True)
    return jsonify(response)


@api_blueprint.route("/<channel_id>/status")
def channel_status(channel_id):
    """From Hub fetch Status"""
    channel = Channel.query.filter_by(channel_id=channel_id).first_or_404()
    response = channel.renew_hub(stringify=True)
    return jsonify(response)


@api_blueprint.route("/<channel_id>/subscribe")
@login_required
def channel_subscribe(channel_id):
    """Subscribe to a Channel"""
    # TODO
    channel = Channel.query.filter_by(channel_id=channel_id).first_or_404()
    return "{}"


@api_blueprint.route("/<channel_id>/unsubscribe")
@login_required
def channel_unsubscribe(channel_id):
    """Unsubscribe to a Channel"""
    # TODO
    channel = Channel.query.filter_by(channel_id=channel_id).first_or_404()
    return "{}"


@api_blueprint.route("/<channel_id>/renew")
@login_required
def channel_renew(channel_id):
    """Renew Subscription Info, Both Hub and Info"""
    channel = Channel.query.filter_by(channel_id=channel_id).first_or_404()
    response = channel.renew(stringify=True)
    return jsonify(response)


@api_blueprint.route("/youtube/subscription")
@login_required
def youtube_subscription():
    """For Dynamically Loading User's YouTube Subscription"""
    get_params = request.args.to_dict()
    try:
        page_token = get_params.pop("page_token")
    except KeyError:
        abort(404)
    response = current_user.youtube.subscriptions().list(
        part="snippet",
        maxResults=50,
        mine=True,
        order="alphabetical",
        pageToken=page_token).execute()
    for channel in response["items"]:
        channel_id = channel["snippet"]["resourceId"]["channelId"]
        channel["snippet"]["subscribed"] = current_user.is_subscribing(
            channel_id)
        channel["snippet"]["subscribe_endpoint"] = url_for(
            "api.channel_subscribe", channel_id=channel_id)
    return jsonify(response)
