import dropbox
from flask import current_app, url_for

# dbx = dropbox.Dropbox(current_app.config["DROPBOX_TOKEN"])

def build_flow(session):
    return dropbox.DropboxOAuth2Flow(
        current_app.config["DROPBOX_APP_KEY"],
        current_app.config["DROPBOX_APP_SECRET"],
        url_for("user.setting_dropbox_oauth_callback", _external=True),
        session,
        current_app.config["SECRET_KEY"])

def build_credentials(credentials):
    return dropbox.oauth.OAuth2FlowResult(
        credentials["access_token"],
        credentials["account_id"],
        credentials["user_id"],
        credentials["url_state"],
    )

def build_service(credentials):
    return dropbox.Dropbox(credentials["access_token"])
