"""YouTube Data API Functions"""
import json
from typing import Union

import youtube_dl
from flask import current_app, url_for
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


def build_flow(state=None):
    """Build Flow Object"""
    with current_app.open_instance_resource(
        current_app.config["YOUTUBE_API_CLIENT_SECRET_FILE"], "r"
    ) as json_file:
        client_config = json.load(json_file)
    flow = Flow.from_client_config(
        client_config,
        scopes=current_app.config["YOUTUBE_READ_WRITE_SSL_SCOPE"],
        state=state,
    )
    flow.redirect_uri = url_for("user.setting_youtube_oauth_callback", _external=True)
    return flow


def build_youtube_api(credentials=None):
    """Build Service with params"""
    kwargs = {}
    if credentials:
        kwargs["credentials"] = Credentials(**credentials)
    else:
        kwargs["developerKey"] = current_app.config["YOUTUBE_API_DEVELOPER_KEY"]

    return build(
        current_app.config["YOUTUBE_API_SERVICE_NAME"],
        current_app.config["YOUTUBE_API_VERSION"],
        cache_discovery=False,
        **kwargs
    )


def build_youtube_dl(additional_options):
    options = {
        "skip_download": True,
        "ignoreerrors": True,
        "extract_flat": True,
    }
    options.update(additional_options)
    return youtube_dl.YoutubeDL(options)


def fetch_video_metadata(video_id: str) -> Union[dict, None]:
    service = build_youtube_dl({"format": "best"})
    metadata = service.extract_info(video_id) or None
    return metadata
