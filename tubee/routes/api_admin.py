from flask import Blueprint, jsonify

from ..models import Callback, Notification

api_admin_blueprint = Blueprint("api_admin", __name__)


@api_admin_blueprint.get("/callbacks")
def callbacks():
    callbacks = Callback.query.order_by(Callback.timestamp.desc()).limit(50)
    return jsonify(callbacks)


@api_admin_blueprint.get("/notifications")
def notifications():
    notifications = (
        Notification.query.order_by(Notification.sent_timestamp.desc()).limit(50).all()
    )
    return jsonify(notifications)
