"""API for Frontend Access"""
from flask import Blueprint, abort, jsonify, request, url_for
from flask_login import current_user, login_required

from ..forms import ActionForm
from ..models import Action
from ..tasks import renew_channels

api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/user/services")
@login_required
def user_info():
    status = {}
    for service in ["youtube", "pushover", "line_notify", "dropbox"]:
        status[service] = bool(getattr(current_user, service))
    return jsonify(status)


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
            details = form.notification.data
            # details = {
            #     "service": "Pushover",
            #     "message": "{video_title}",
            #     "title": "New from {channel_name}",
            #     "url": "https://www.youtube.com/watch?v={video_id}",
            #     "url_title": "{video_title}",
            #     "image_url": "{video_thumbnails}",
            # }
        elif form.action_type.data == "Playlist":
            details = form.playlist.data
            # details = {"playlist_id": "WL"}
        elif form.action_type.data == "Download":
            details = form.download.data
            # details = {"file_path": "/{video_title}.mp4"}
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
            "api_channel.subscribe", channel_id=channel_id
        )
    return jsonify(response)
