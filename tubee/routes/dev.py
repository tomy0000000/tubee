"""Routes for Developing/Testing"""
import os
import sys
import pprint
from flask import Blueprint, current_app, render_template, url_for
from flask_login import current_user, login_required
from .. import login_manager, scheduler
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
    return render_template("map.html", links=links)

@dev_blueprint.route("/os")
@login_required
@admin_required
def os_dict():
    target_dict = os.environ.__dict__
    # target_dict = os.environ["SECURITYSESSIONID"]
    # target_dict = os.environ["TERM_SESSION_ID"]+"</br>"+os.environ["ITERM_SESSION_ID"]
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
    # target_dict["apscheduler"] = target_dict["apscheduler"].__dict__
    # target_dict["apscheduler"]["_scheduler"] = target_dict["apscheduler"]["_scheduler"].__dict__
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

@dev_blueprint.route("/scheduler")
@login_required
@admin_required
def scheduler_dict():
    target_dict = scheduler.__dict__
    # target_dict["_scheduler"] = scheduler.scheduler.__dict__
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

@dev_blueprint.route("/instance")
@login_required
@admin_required
def instance():
    # instances_set = redis_store.smembers("INSTANCE_SET")
    # instances_list = [instance.decode("utf-8") for instance in instances_set]
    # response = "Instance ID: " + current_app.config["INSTANCE_ID"] + "\n" + \
    #             "Session ID: " + redis_store.get("SESSION_ID").decode("utf-8") + "\n" + \
    #             "Active Instances: " + "\n" + \
    #             pprint.pformat(instances_list)
    response = id(current_app)
    current_app.logger.info(response)
    return render_template("empty.html", info=response, pprint=True)

@dev_blueprint.route("/empty")
def empty():
    return render_template("empty.html")

@dev_blueprint.route("/debugger")
def debugger():
    pass

from . import tmp
