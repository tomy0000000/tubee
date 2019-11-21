"""Routes for Developing/Testing"""
import os
import sys
import pprint
from flask import abort, Blueprint, current_app, render_template, url_for
from flask_login import current_user, login_required
from .. import login_manager
from ..helper import admin_required
dev_blueprint = Blueprint("dev", __name__)

@dev_blueprint.route("generate_url")
@login_required
def generate_url():
    return render_template("empty.html", info=url_for("dev.sitemap", _external=True))

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
    return render_template("map.html", links=links)

@dev_blueprint.route("/os")
@login_required
@admin_required
def os_dict():
    target_dict = os.environ.__dict__
    pprint_en = isinstance(target_dict, dict)
    if pprint_en:
        target_dict = pprint.pformat(target_dict)
    return render_template("empty.html", info=target_dict, pprint=pprint_en)

@dev_blueprint.route("/sys")
@login_required
@admin_required
def sys_dict():
    target_dict = sys.__dict__
    target_dict = sys.thread_info.__dict__
    pprint_en = isinstance(target_dict, dict)
    if pprint_en:
        target_dict = pprint.pformat(target_dict)
    return render_template("empty.html", info=target_dict, pprint=pprint_en)

@dev_blueprint.route("/flask")
@login_required
@admin_required
def flask_dict():
    target_dict = current_app.__dict__
    pprint_en = isinstance(target_dict, dict)
    if pprint_en:
        target_dict = pprint.pformat(target_dict)
    return render_template("empty.html", info=target_dict, pprint=pprint_en)

@dev_blueprint.route("/login-manager")
@login_required
@admin_required
def login_manager_dict():
    target_dict = login_manager.__dict__
    pprint_en = isinstance(target_dict, dict)
    if pprint_en:
        target_dict = pprint.pformat(target_dict)
    return render_template("empty.html", info=target_dict, pprint=pprint_en)

@dev_blueprint.route("/user")
@login_required
@admin_required
def user_dict():
    target_dict = current_user.__dict__
    pprint_en = isinstance(target_dict, dict)
    if pprint_en:
        target_dict = pprint.pformat(target_dict)
    return render_template("empty.html", info=target_dict, pprint=pprint_en)

@dev_blueprint.route("/empty")
def empty():
    return render_template("empty.html")

@dev_blueprint.route("/debugger")
def debugger():
    pass

@dev_blueprint.route("/handler/<status_code>")
@login_required
@admin_required
def handler(status_code):
    abort(int(status_code))

from . import tmp
