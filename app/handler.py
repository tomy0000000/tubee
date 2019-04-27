"""Error Handler for Tubee"""
from datetime import datetime
import sqlalchemy.exc
from flask import request, render_template, Blueprint
from . import db
# from Tubee.helper import send_notification
from .models import Request
handler_blueprint = Blueprint("handler", __name__)

@handler_blueprint.errorhandler(404)
def page_not_found(error):
    """Raised when Page Not Found"""
    # send_notification("404 Alert", str(datetime.now()),
    #                   title="Tubee received an 404 Error!!")
    return render_template("error.html", error=error), 404

@handler_blueprint.errorhandler(sqlalchemy.exc.OperationalError)
def sql_error(error):
    """Raised when SQL Access Failed"""
    return render_template("empty.html", content=error), 500

# @app.after_request
# def after_request(response):
#     new = Request(request.method, request.scheme, request.host,
#                   request.path, request.args, request.data,
#                   response.status_code, request.user_agent)
#     db.session.add(new)
#     try:
#         db.session.commit()
#         # send_notification("after_request", str(new))
#     except Exception as e:
#         send_notification("SQL Error", str(datetime.now())+"\n"+str(e),
#                           title="Tubee encontered a SQL Error!!")
#     return response
