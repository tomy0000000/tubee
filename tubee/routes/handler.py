"""Error Handlers"""
import traceback

from flask import Blueprint, current_app, flash, jsonify, render_template, request
from flask_login import current_user
from googleapiclient.errors import HttpError as YouTubeHttpError
from werkzeug.exceptions import HTTPException as WerkzeugHTTPException

handler_blueprint = Blueprint("handler", __name__)


@handler_blueprint.app_errorhandler(Exception)
def unhandled_exception(error):
    """
    https://werkzeug.palletsprojects.com/en/1.0.x/exceptions/#error-classes
    """

    # Log error to traceback if error is not triggered intentionally
    if isinstance(error, WerkzeugHTTPException):
        code = error.code
    else:
        code = 500

    if isinstance(error, YouTubeHttpError) and "quota" in str(error):
        current_app.logger.info(f"YouTube API Quota exceed: {error}")
    current_app.logger.getChild("error").exception("Error")

    # Return an error response to user
    if request.path.startswith("/api"):
        return jsonify({"code": code, "description": str(error)}), code
    if current_user.is_authenticated and current_user.admin:
        flash(traceback.format_exc(), "danger")
    else:
        flash(error, "danger")
    return render_template("error.html"), code
