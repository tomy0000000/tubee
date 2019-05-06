"""API for Frontend Access"""
from flask import Blueprint
from .. import scheduler
api = Blueprint("api", __name__)

@api.route("/scheduler/pause_job")
def scheduler_pause_job():
    """Pause Specific Scheduled Job"""
    response = scheduler.get_job("test").pause()
    return response
