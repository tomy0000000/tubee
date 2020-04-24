"""Dropbox Related Functions"""
import dropbox
from flask import current_app, url_for


def build_flow(session):
    return dropbox.DropboxOAuth2Flow(
        current_app.config["DROPBOX_APP_KEY"],
        current_app.config["DROPBOX_APP_SECRET"],
        url_for("user.setting_dropbox_oauth_callback", _external=True),
        session,
        current_app.config["SECRET_KEY"],
    )


# def save_file_to_dropbox(user, file_path):
#     service = dropbox.Dropbox(user.dropbox_credentials["access_token"])
#     with open(file_path, "rb") as file:
#         try:
#             filename = os.path.basename(file_path)
#             metadata = service.files_upload(
#                 file.read(),
#                 "/{}".format(filename),
#                 mode=dropbox.files.WriteMode("overwrite"))
#             return (True, metadata)
#         except dropbox.exceptions.ApiError as err:
#             # This checks for the specific error where a user doesn't have
#             # enough Dropbox space quota to upload this file
#             if (err.error.is_path()
#                     and err.error.get_path().reason.is_insufficient_space()):
#                 return (False, "insufficient space")
#             if err.user_message_text:
#                 return (False, err.user_message_text)
#             return (False, err)


# def save_url_to_dropbox(user, url, filename):
#     service = dropbox.Dropbox(user.dropbox_credentials["access_token"])
#     metadata = service.files_save_url("/{}".format(filename), url)
#     return (True, metadata)
