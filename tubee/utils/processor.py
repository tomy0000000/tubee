from flask import flash, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

from .. import db, models
from ..exceptions import TubeeError
from . import build_sitemap


def shell():
    return dict(db=db, models=models)


def template():
    return dict(sitemap=build_sitemap())


def error_handler(error):
    """Handle Errors

    Arguments:
        error {Exception} -- The error to be handled

    Returns:
        Response -- Wrapped response
    """
    name = error.__class__.__name__
    if isinstance(error, HTTPException):  # raised with flask.abort(code, description)
        description = str(error.description)
        status_code = error.code
    elif isinstance(error, TubeeError):
        description = str(error.description)
        status_code = 400
    else:
        name = None  # hide internal errors from user
        description = "Internal Server Error"
        status_code = 500

    if request.path.startswith("/api"):
        response = dict(ok=False, error=name, description=description)
        return jsonify(response), status_code

    flash(f"{name}: {description}", "danger")
    return render_template("error.html"), status_code


def api_formatter(response):
    """Format API Response

    Arguments:
        response {Response} -- The response to be formatted

    Returns:
        Response -- Wrapped JSON response
    """
    content = response.get_json()
    if "error" in content or "datatable" in content:
        return response
    formatted_response = jsonify(ok=True, error=None, description=None, content=content)
    return formatted_response
