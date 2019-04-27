"""Initialization of Tubee"""
import atexit
import codecs
import flask
import flask_apscheduler
import flask_bcrypt
import flask_login
import flask_migrate
import flask_redis
import flask_sqlalchemy
import time
import httplib2
import json
import logging.config
# import mod_wsgi
import os
import pushover_complete
import sys
from apiclient import discovery
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
# from app.helper import build_internal_scheduler
from config import config

# def build_internal_scheduler():
#     jobstores_meta = {
#         "default": SQLAlchemyJobStore(engine=db.engine)
#     }
#     return BackgroundScheduler(jobstores=jobstores_meta)

db = flask_sqlalchemy.SQLAlchemy()              # flask_sqlalchemy
scheduler = flask_apscheduler.APScheduler()     # flask_apscheduler
login_manager = flask_login.LoginManager()      # flask_login
bcrypt = flask_bcrypt.Bcrypt()                  # flask_bcrypt
redis_store = flask_redis.Redis()               # flask_redis

# Main Application
# app = flask.Flask(__name__, instance_relative_config=True)
# app.config.from_object(config["default"])
# if os.path.isfile(os.path.join(app.instance_path, "tmpconfig.py")):
#     app.config.from_pyfile("tmpconfig.py")
# if "LOGGING_CONFIG" in app.config:
#     logging.config.dictConfig(app.config["LOGGING_CONFIG"])

# Plugins
# with app.app_context():
#     db.init_app(app)
#     scheduler.scheduler.add_jobstore(SQLAlchemyJobStore(engine=db.engine))
#     scheduler.init_app(app)



# pusher = pushover_complete.PushoverAPI(config["default"].PUSHOVER_TOKEN)        # Pushover

# # YouTube DATA API Configurations
# YouTube_Service_Public = discovery.build(
#     config["default"].YOUTUBE_API_SERVICE_NAME,
#     config["default"].YOUTUBE_API_VERSION,
#     cache_discovery=False,
#     developerKey=config["default"].YOUTUBE_API_DEVELOPER_KEY)

# System Global Registration
# scheduler.start()
# app.logger.info("Scheduler Started")
# app.config["INSTANCE_ID"] = generate_random_id()
# app.config["INSTANCE_ID"] = codecs.encode(os.urandom(16), "hex").decode()
# previous_session_id = redis_store.get("SESSION_ID")
# previous_session_id = previous_session_id.decode("utf-8") if previous_session_id else ""
# if previous_session_id == os.environ.get("INVOCATION_ID"):
#     app.logger.info(app.config["INSTANCE_ID"]+": Instance built WITHOUT scheduler start")
# else:
#     redis_store.set("SESSION_ID", os.environ.get("INVOCATION_ID"))
#     redis_store.delete("INSTANCE_SET")
#     scheduler.start()
#     app.logger.info(os.environ.get("INVOCATION_ID")+": Session Registed")
#     app.logger.info(app.config["INSTANCE_ID"]+": Instance built WITH scheduler start")
# redis_store.sadd("INSTANCE_SET", app.config["INSTANCE_ID"])

# @atexit.register
# def unregister():
#     redis_store.srem("INSTANCE_SET", app.config["INSTANCE_ID"])
#     app.logger.info(app.config["INSTANCE_ID"]+": Instance shutdown")

# from . import views, handler

def create_app(config_name):
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    if os.path.isfile(os.path.join(app.instance_path, "tmpconfig.py")):
        app.config.from_pyfile("tmpconfig.py")
    if "LOGGING_CONFIG" in app.config:
        logging.config.dictConfig(app.config["LOGGING_CONFIG"])

    db.init_app(app)
    
    if config_name != "default":
        return app

    # with app.app_context():
        # scheduler.scheduler.remove_jobstore("default")
        # scheduler.scheduler.add_jobstore(SQLAlchemyJobStore(engine=db.engine), "inited")
    scheduler.init_app(app)

    bcrypt.init_app(app)
    login_manager.init_app(app)
    if app.config["REDIS_PASSWORD"]:
        redis_store.init_app(app)

    scheduler.start()
    app.logger.info("Scheduler Started")

    from app.views import route_blueprint
    app.register_blueprint(route_blueprint)
    from app.handler import handler_blueprint
    app.register_blueprint(handler_blueprint)

    return app

_shallow_app = create_app("development")

# Pushover
pusher = pushover_complete.PushoverAPI(_shallow_app.config["PUSHOVER_TOKEN"])

# YouTube DATA API Configurations
YouTube_Service_Public = discovery.build(
    _shallow_app.config["YOUTUBE_API_SERVICE_NAME"],
    _shallow_app.config["YOUTUBE_API_VERSION"],
    cache_discovery=False,
    developerKey=_shallow_app.config["YOUTUBE_API_DEVELOPER_KEY"])
