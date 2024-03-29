"""API for Tasks"""
from flask import Blueprint, jsonify
from flask_login import login_required

from ..tasks import channels_renew, list_all_tasks, remove_all_tasks
from ..utils import admin_required

api_task_blueprint = Blueprint("api_task", __name__)
api_task_blueprint.before_request(admin_required)


@api_task_blueprint.get("/list-all")
@login_required
def list_all():
    response = list_all_tasks()
    return jsonify(response)


@api_task_blueprint.get("/remove-all")
@login_required
def remove_all():
    response = remove_all_tasks()
    return response


@api_task_blueprint.get("/<task_id>/status")
@login_required
def status(task_id):
    task = channels_renew.AsyncResult(task_id)
    response = {
        "id": task.id,
        "status": task.status.title(),
        "result": task.result,
        "traceback": task.traceback,
    }
    print(f"{response=}")
    if isinstance(task.result, Exception):
        response["result"] = str(task.result)
        response["traceback"] = task.__dict__["_cache"]["traceback"]
    else:
        response["current"] = task.result.get("current", 1)
        response["total"] = task.result.get("total", 1)
        response["channel_id"] = task.result.get("channel_id", None)
    return response
