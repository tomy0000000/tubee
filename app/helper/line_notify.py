"""Line Notify Related Functions"""
from flask import current_app, abort
from flask_login import current_user

def build_service(oauth):
    # TODO: This Results in context issue, fix this someday
    # with current_app.app_context():
    #     if "LINENOTIFY_CLIENT_ID" not in current_app.config:
    #         current_app.logger.info("Line Notify Client ID hasn't configured")
    #         abort(500)
    #     if "LINENOTIFY_CLIENT_SECRET" not in current_app.config:
    #         current_app.logger.info("Line Notify Client Secret hasn't configured")
    #         abort(500)
    oauth.register(
        name="LineNotify",
        api_base_url="https://notify-api.line.me/",
        authorize_url="https://notify-bot.line.me/oauth/authorize",
        authorize_params={
            "response_type": "code",
            "scope": "notify"
        },
        access_token_url="https://notify-bot.line.me/oauth/token",
        fetch_token=fetch_token
    )

def fetch_token():
    return current_user.get_line_notify_credentials()
