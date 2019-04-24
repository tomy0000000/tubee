"""Initialization of FlaskApp"""
import atexit
import codecs
import flask
import flask_apscheduler
import flask_bcrypt
import flask_login
import flask_migrate
import flask_redis
import flask_sqlalchemy
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

def build_internal_scheduler():
    jobstores_meta = {
        "default": SQLAlchemyJobStore(engine=db.engine)
    }
    return BackgroundScheduler(jobstores=jobstores_meta)

# Main Application
app = flask.Flask(__name__, instance_relative_config=True)
app.config.from_object(config["default"])
if os.path.isfile(os.path.join(app.instance_path, "tmpconfig.py")):
    app.config.from_pyfile("tmpconfig.py")
# app.config.from_envvar("TUBEE_CONFIG_FILE")
if "LOGGING_CONFIG" in app.config:
    logging.config.dictConfig(app.config["LOGGING_CONFIG"])

# Plugins
db = flask_sqlalchemy.SQLAlchemy(app)                                       # flask_sqlalchemy
scheduler = flask_apscheduler.APScheduler(build_internal_scheduler(), app)  # flask_apscheduler
bcrypt = flask_bcrypt.Bcrypt(app)                                           # flask_bcrypt
login_manager = flask_login.LoginManager(app)                               # flask_login
migrate = flask_migrate.Migrate(app, db)                                    # flask_migrate
if app.config["REDIS_PASSWORD"]:
    redis_store = flask_redis.Redis(app)  # flask_redis
pusher = pushover_complete.PushoverAPI(app.config["PUSHOVER_TOKEN"])        # Pushover

app.db = db
app.pusher = pusher

# YouTube DATA API Configurations
YouTube_Service_Public = discovery.build(
    app.config["YOUTUBE_API_SERVICE_NAME"],
    app.config["YOUTUBE_API_VERSION"],
    cache_discovery=False,
    developerKey=app.config["YOUTUBE_API_DEVELOPER_KEY"])

# System Global Registration
scheduler.start()
app.logger.info("Scheduler Started")
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

from app import views, handler
# @app.route("/dev_empty")
# def dev_empty():
#     return render_template("empty.html")
if __name__ == "__main__":
    app.run(host="0.0.0.0")
