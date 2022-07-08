from flask import Blueprint, jsonify

from ..models import Callback, Channel, Notification

api_admin_blueprint = Blueprint("api_admin", __name__)


@api_admin_blueprint.route("/channels")
def channel():
    channels = Channel.query.all()
    return jsonify(channels)


@api_admin_blueprint.route("/callbacks")
def callbacks():
    callbacks = Callback.query.order_by(Callback.timestamp.desc()).limit(50)
    return jsonify(callbacks)


@api_admin_blueprint.route("/notifications")
def notifications():
    notifications = Notification.query.order_by(
        Notification.sent_timestamp.desc()
    ).limit(50)
    return jsonify(notifications)
