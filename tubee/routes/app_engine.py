"""API endpoint which only loads when using Google App Engine"""
import logging
from flask import Blueprint, abort, current_app, jsonify, request
from flask_migrate import Migrate, upgrade
from ..helper import (
    app_engine_required,
    notify_admin,
)

app_engine_blueprint = Blueprint("app_engine", __name__)


@app_engine_blueprint.route("/deploy")
def deploy():
    """Run deployment tasks."""

    # Verify Key
    server_key = current_app.config["DEPLOY_KEY"]
    client_key = request.args.to_dict().get("key")
    if not server_key:
        logging.info("Deploy triggered without server key")
    if not client_key:
        logging.info("Deploy triggered without client key")
    if server_key != client_key:
        logging.info("Deploy triggered but keys don't matched")
    if not server_key or not client_key or server_key != client_key:
        abort(401)

    # Run tasks, notify admins if anything went wrong
    try:
        # migrate database to latest revision
        migrate = Migrate(current_app, current_app.db, render_as_batch=True)
        upgrade()
        response = "Deployment Task Completed"
    except Exception as error:
        response = notify_admin(
            "Deployment", "Pushover", message=error, title="Deployment Error"
        )
    return jsonify(response)


@app_engine_blueprint.route("/channels/renew", methods=["POST"])
@app_engine_required
def channels_renew():
    payload = request.get_data(as_text=True)
    response = payload
    notify_admin(
        "Cron Renew", "Pushover", message=response, title="Cron Renew Triggered"
    )
    return jsonify(response)
