from typing import Union

from flask import Response, current_app, flash, jsonify, render_template, request
from loguru import logger
from werkzeug.exceptions import HTTPException

from .. import db, models
from ..exceptions import TubeeError
from . import build_sitemap


def shell():
    return dict(db=db, models=models)


def template():
    return dict(sitemap=build_sitemap())


def error_handler(error) -> tuple[Union[Response, str], int]:
    """Handle Errors

    Arguments:
        error {Exception} -- The error to be handled

    Returns:
        Response -- Wrapped response
    """
    name = error.__class__.__name__

    if isinstance(error, HTTPException):  # raised with flask.abort(code, description)
        description = f"{name}: {error.description}"
        status_code = error.code or 400
    elif isinstance(error, TubeeError):
        description = f"{name}: {error.description}"
        status_code = 400
    else:
        description = "Internal Server Error"  # hide internal errors from user
        status_code = 500
        logger.exception(name)  # log internal errors

    if request.path.startswith("/api"):
        response = dict(ok=False, error=name, description=description)
        return jsonify(response), status_code

    if current_app.debug:
        raise error  # So the debugger shows up

    flash(description, "danger")
    return render_template("error.html"), status_code


def api_formatter(response: Response):
    """Format API Response

    Arguments:
        response {Response} -- The response to be formatted

    Returns:
        Response -- Wrapped JSON response
    """
    content = response.get_json()
    if isinstance(content, dict) and ("error" in content or "datatable" in content):
        return response
    formatted_response = jsonify(ok=True, error=None, description=None, content=content)
    return formatted_response
