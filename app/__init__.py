"""Main Application of Tubee"""
import atexit
import codecs
import json
import logging.config
import os
import sys

import flask
from authlib.flask.client import OAuth
from flask_apscheduler import APScheduler
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_moment import Moment
from flask_redis import Redis
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from config import config

# TODO: TRY IMPLEMENT IN ANOTHER WAY
naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=naming_convention)
oauth = OAuth()                                             # authlib
scheduler = APScheduler()                                   # flask_apscheduler
bcrypt = Bcrypt()                                           # flask_bcrypt
login_manager = LoginManager()                              # flask_login
moment = Moment()                                           # flask_moment
redis_store = Redis()                                       # flask_redis
db = SQLAlchemy(metadata=metadata)                          # flask_sqlalchemy

def create_app(config_name):
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    if os.path.isfile(os.path.join(app.instance_path, "logging.cfg")):
        with app.open_instance_resource("logging.cfg", "r") as json_file:
            logging.config.dictConfig(json.load(json_file))

    db.init_app(app)
    app.db = db
    db.app = app
    config[config_name].init_app(app)
    oauth.init_app(app)
    from .helper.line_notify import build_service
    build_service(oauth)
    scheduler.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    if app.config["REDIS_HOST"]:
        redis_store.init_app(app)
        app.logger.info("Redis Initialized")
    if config_name != "testing":
        scheduler.start()
        app.logger.info("Scheduler Started")
    
    # System Global Registration
    # scheduler.start()
    # app.logger.info("Scheduler Started")
    # app.config["INSTANCE_ID"] = generate_random_id()
    # with app.app_context():
    #     app.config["INSTANCE_ID"] = codecs.encode(os.urandom(16), "hex").decode()
    #     process_uuid = redis_store.get("PROCESS_UUID")
    #     process_uuid = process_uuid.decode("utf-8") if process_uuid else ""
    #     # thread_uuid = os.environ.get("INVOCATION_ID")
    #     thread_uuid = id(app)
    #     if process_uuid == thread_uuid:
    #         app.logger.info(app.config["INSTANCE_ID"]+": Instance built WITHOUT scheduler start")
    #     else:
    #         redis_store.set("PROCESS_UUID", thread_uuid)
    #         redis_store.delete("INSTANCE_SET")
    #         scheduler.start()
    #         app.logger.info(thread_uuid+": Session Registed")
    #         app.logger.info(app.config["INSTANCE_ID"]+": Instance built WITH scheduler start")
    #     redis_store.sadd("INSTANCE_SET", app.config["INSTANCE_ID"])

    #     @atexit.register
    #     def unregister():
    #         redis_store.srem("INSTANCE_SET", app.config["INSTANCE_ID"])
    #         app.logger.info(app.config["INSTANCE_ID"]+": Instance shutdown")

    from .routes.main import main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes.admin import admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix="/admin")

    from .routes.api import api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/api")

    from .routes.channel import channel_blueprint
    app.register_blueprint(channel_blueprint, url_prefix="/channel")

    from .routes.dev import dev_blueprint
    app.register_blueprint(dev_blueprint, url_prefix="/dev")

    from .routes.user import user_blueprint
    app.register_blueprint(user_blueprint, url_prefix="/user")

    from .handler import handler
    app.register_blueprint(handler)

    return app
