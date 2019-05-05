"""Error Handler for Tubee"""
import sqlalchemy.exc
from flask import Blueprint, render_template
handler_blueprint = Blueprint("handler", __name__)

@handler_blueprint.errorhandler(404)
def page_not_found(error):
    """Raised when Page Not Found"""
    return render_template("error.html", error=error), 404

@handler_blueprint.errorhandler(sqlalchemy.exc.OperationalError)
def sql_error(error):
    """Raised when SQL Access Failed"""
    return render_template("empty.html", content=error), 500
