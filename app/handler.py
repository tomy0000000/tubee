"""Error Handler for Tubee"""
import MySQLdb
import sqlalchemy.exc
from flask import Blueprint, current_app, redirect, render_template, session, url_for
from . import db, login_manager
handler = Blueprint("handler", __name__)

@login_manager.unauthorized_handler
def not_logined():
    session["login_message_body"] = "You Must Login First"
    session["login_message_type"] = "warning"
    return redirect(url_for("user.login"))

@handler.app_errorhandler(401)
def unauthorized(alert):
    """Raised when User didn't logined yet"""
    return render_template("error.html", alert=alert, alert_float=True), 401

@handler.app_errorhandler(403)
def forbidden(alert):
    """Raised when User did login, but didn't had the permission"""
    return render_template("error.html", alert=alert, alert_float=True), 403

@handler.app_errorhandler(404)
def page_not_found(alert):
    """Raised when Page Not Found"""
    return render_template("error.html", alert=alert, alert_float=True), 404

@handler.app_errorhandler(500)
def page_not_found(alert):
    """Raised when Page Not Found"""
    return render_template("error.html", alert=alert, alert_float=True), 500

@handler.app_errorhandler(501)
def page_not_found(alert):
    """Raised when Page Not Found"""
    return render_template("error.html", alert=alert, alert_float=True), 501

@handler.app_errorhandler(502)
def page_not_found(alert):
    """Raised when Page Not Found"""
    return render_template("error.html", alert=alert, alert_float=True), 502

# @handler.app_errorhandler(MySQLdb.Error)
# @handler.app_errorhandler(MySQLdb._exceptions.OperationalError)
# @handler.app_errorhandler(sqlalchemy.exc.StatementError)
# @handler.app_errorhandler(sqlalchemy.exc.InvalidRequestError)
# def sql_error(alert):
#     """Raised when SQL Access Failed"""
#     return render_template("error.html", alert=alert), 500

# @handler.before_app_first_request
# @handler.app_errorhandler(sqlalchemy.exc.OperationalError)
# def session():
#     """Try rollback session"""
#     try:
#         db.session.rollback()
#     except Exception as e:
#         raise e

# @handler.app_errorhandler(Exception)
# def unhandled_exception(error):
#     current_app.logger.error("Unhandled Exception: {}".format(error))
#     return render_template("error.html", alert=error), 500
