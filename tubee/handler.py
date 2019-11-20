"""Error Handlers"""
from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.exceptions import HTTPException
from . import login_manager
handler = Blueprint("handler", __name__)


@login_manager.unauthorized_handler
def not_logined():
    session["login_message_body"] = "You Must Login First"
    session["login_message_type"] = "warning"
    return redirect(url_for("user.login"))


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
    current_app.logger.error(error)
    if request.path.startswith("/api"):
        return jsonify({"code": code, "description": str(error)}), code
    return render_template("error.html", alert=error), code
