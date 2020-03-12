"""Error Handlers"""
import traceback
from flask import (
    Blueprint,
    flash,
    jsonify,
    render_template,
    request,
)
from flask_login import current_user
from werkzeug.exceptions import HTTPException
handler = Blueprint("handler", __name__)


@handler.app_errorhandler(Exception)
def unhandled_exception(error):
    """
    401: Raised when User didn't logined yet
    403: Raised when User did login, but didn't had the permission
    404: Raised when page can not be found
    405: Raised when endpoint is visited with wrong method
    406: Raised when response content doesn't fit headers requirement
    500: Raised when something went wrong unexpectedly
    501: Raised when the endpoint is not implemented yet
    https://werkzeug.palletsprojects.com/en/0.16.x/exceptions/#error-classes
    """
    code = error.code if isinstance(error, HTTPException) else 500
    # current_app.logger.error(traceback.format_exc())
    if request.path.startswith("/api"):
        return jsonify({"code": code, "description": str(error)}), code
    if current_user.is_authenticated and current_user.admin:
        flash(traceback.format_exc(), "danger")
    else:
        flash(error, "danger")
    return render_template("error.html"), code
