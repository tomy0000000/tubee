from flask import Blueprint, jsonify

from ..models import Callback

api_admin_blueprint = Blueprint("api_admin", __name__)


@api_admin_blueprint.get("/callbacks")
def callbacks():
    callbacks = Callback.query.order_by(Callback.timestamp.desc()).limit(50)
    return jsonify(callbacks)
