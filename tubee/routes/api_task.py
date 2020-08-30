"""API for Tasks"""
from flask import Blueprint, jsonify
from flask_login import login_required

from .. import celery
from ..helper import admin_required
from ..tasks import renew_channels

api_task_blueprint = Blueprint("api_task", __name__)


@api_task_blueprint.route("/list-scheduled")
@login_required
@admin_required
def list_scheduled():
    worker_scheduled = celery.control.inspect().scheduled()
    if worker_scheduled:
        tasks = [task for worker in worker_scheduled.values() for task in worker]
    else:
        tasks = []
    return jsonify(tasks)


@api_task_blueprint.route("/list-revoked")
@login_required
@admin_required
def list_revoked():
    worker_revoked = celery.control.inspect().revoked()
    if worker_revoked:
        revoked_tasks = [task for worker in worker_revoked.values() for task in worker]
    else:
        revoked_tasks = []
    return jsonify(revoked_tasks)


@api_task_blueprint.route("/list-all")
@login_required
@admin_required
def list_all():
    worker_scheduled = celery.control.inspect().scheduled()
    if not worker_scheduled:
        return jsonify([])
    worker_revoked = celery.control.inspect().revoked()
    if worker_revoked:
        revoked_tasks = [task for worker in worker_revoked.values() for task in worker]
    else:
        revoked_tasks = []
    tasks = []
    for worker in worker_scheduled.values():
        for task in worker:
            if task["request"]["id"] not in revoked_tasks:
                tasks.append(task)
    return jsonify(tasks)


@api_task_blueprint.route("/remove-all")
@login_required
@admin_required
def remove_all():
    worker_tasks = celery.control.inspect().scheduled()
    if not worker_tasks:
        return jsonify(None)
    results = {"removed": [], "error": {}}
    for worker in worker_tasks.values():
        for task in worker:
            try:
                task_id = task["request"]["id"]
                celery.control.revoke(task_id)
                results["removed"].append(task)
            except Exception as error:
                results["error"][task_id] = str(error)
    return jsonify(results)


@api_task_blueprint.route("/<task_id>/status")
@login_required
@admin_required
def status(task_id):
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
