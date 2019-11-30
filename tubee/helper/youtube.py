"""YouTube Data API Functions"""
import json
from flask import current_app, url_for
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow


def build_flow(state=None):
    """Build Flow Object"""
    with current_app.open_instance_resource(
            current_app.config["YOUTUBE_API_CLIENT_SECRET_FILE"],
            "r") as json_file:
        client_config = json.load(json_file)
    flow = Flow.from_client_config(
        client_config,
        current_app.config["YOUTUBE_READ_WRITE_SSL_SCOPE"],
        state=state)
    flow.redirect_uri = url_for("user.setting_youtube_oauth_callback",
                                _external=True)
    return flow


def build_service(credentials=None):
    """Build Service with params"""
    kwargs = {}
    if credentials:
        kwargs["credentials"] = Credentials(**credentials)
    else:
        kwargs["developerKey"] = current_app.config[
            "YOUTUBE_API_DEVELOPER_KEY"]

    return build(current_app.config["YOUTUBE_API_SERVICE_NAME"],
                 current_app.config["YOUTUBE_API_VERSION"],
                 cache_discovery=False,
                 **kwargs)


def auto_renew(channel):
    """Trigger Channel Renewal"""
    response = channel.renew()
    current_app.logger.info(
        "----------------Auto Renewed Start----------------")
    current_app.logger.info("{}<{}>".format(channel.channel_name,
                                            channel.channel_id))
    current_app.logger.info(response)
    current_app.logger.info(
        "--------------Auto Renewed Complete--------------")
    return response
