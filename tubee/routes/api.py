"""API for Frontend Access"""
from flask import Blueprint
from flask_login import current_user, login_required

from tubee.exceptions import ServiceNotAuth

api_blueprint = Blueprint("api", __name__)


@api_blueprint.get("/user/services")
@login_required
def user_services():
    response = {}
    for service in ["youtube", "pushover", "line_notify", "dropbox"]:
        try:
            response[service] = bool(getattr(current_user, service))
        except ServiceNotAuth:
            response[service] = False
    return response
