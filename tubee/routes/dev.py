"""Routes for Developing/Testing"""
import pprint
from flask import abort, Blueprint, current_app, render_template, request, url_for
from flask_login import current_user, login_required
from ..helper import admin_required
dev_blueprint = Blueprint("dev", __name__)


@dev_blueprint.route("/sitemap")
@login_required
@admin_required
def sitemap():
    links = []
    for rule in current_app.url_map.iter_rules():
        query = {arg: "[{0}]".format(arg) for arg in rule.arguments}
        url = url_for(rule.endpoint, **query)
        links.append((url, rule.endpoint))
    links.sort(key=lambda x: x[1])
    return render_template("sitemap.html", links=links)


@dev_blueprint.route("/request")
@login_required
@admin_required
def request_dict():
    target_dict = request.__dict__
    pprint_en = isinstance(target_dict, dict)
    if pprint_en:
        target_dict = pprint.pformat(target_dict)
    return render_template("empty.html", info=target_dict, pprint=pprint_en)


@dev_blueprint.route("/user")
@login_required
@admin_required
def user_dict():
    # target_dict = current_user.__dict__
    target_dict = {
        "is_authenticated": current_user.is_authenticated,
        "is_active": current_user.is_active,
        "is_anonymous": current_user.is_anonymous,
        "get_id()": current_user.get_id(),
    }
    pprint_en = isinstance(target_dict, dict)
    if pprint_en:
        target_dict = pprint.pformat(target_dict)
    return render_template("empty.html", info=target_dict, pprint=pprint_en)


@dev_blueprint.route("/empty")
def empty():
    return render_template("empty.html")


@dev_blueprint.route("/handler/<status_code>")
@login_required
@admin_required
def handler(status_code):
    abort(int(status_code))


from . import tmp
