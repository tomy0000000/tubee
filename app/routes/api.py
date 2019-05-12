"""API for Frontend Access"""
from flask import Blueprint
from flask_login import login_required
from .. import scheduler
from ..models import Subscription
api = Blueprint("api", __name__)

@api.route("/scheduler/pause_job")
def scheduler_pause_job():
    """Pause Specific Scheduled Job"""
    response = scheduler.get_job("test").pause()
    return response

@api.route("/<channel_id>/status")
def channel_status(channel_id):
    """From Hub fetch Status"""
    subscription = Subscription.query.filter_by(channel_id=channel_id).first_or_404()
    response = subscription.get_hub_details()
    return response.text

@api.route("/<channel_id>/subscribe")
@login_required
def api_channel_subscribe():
    """Subscribe to a Channel"""
    # TODO
    return "{}"

@api.route("/<channel_id>/unsubscribe")
@login_required
def api_channel_unsubscribe():
    """Unsubscribe to a Channel"""
    # TODO
    return "{}"
