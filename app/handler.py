"""Error Handler for Tubee"""
import sqlalchemy.exc
from flask import Blueprint, redirect, render_template, session, url_for
from . import login_manager
handler = Blueprint("handler", __name__)

@login_manager.unauthorized_handler
def not_logined():
    session["login_message_body"] = "You Must Login First"
    session["login_message_type"] = "warning"
    return redirect(url_for("user.login"))

@handler.app_errorhandler(401)
def unauthorized(alert):
    """Raised when User didn't logined yet"""
    return render_template("error.html", alert=alert), 401

@handler.app_errorhandler(403)
def forbidden(alert):
    """Raised when User did login, but didn't had the permission"""
    return render_template("error.html", alert=alert), 403

@handler.app_errorhandler(404)
def page_not_found(alert):
    """Raised when Page Not Found"""
    return render_template("error.html", alert=alert), 404

@handler.app_errorhandler(sqlalchemy.exc.OperationalError)
def sql_error(alert):
    """Raised when SQL Access Failed"""
    return render_template("error.html", alert=alert), 500
