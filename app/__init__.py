"""Main Application of Tubee"""
import atexit
import codecs
import flask
import flask_apscheduler
import flask_bcrypt
import flask_login
import flask_redis
import flask_sqlalchemy
import json
import logging.config
import os
import sys
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
metadata=MetaData(naming_convention=naming_convention)
db = flask_sqlalchemy.SQLAlchemy(metadata=metadata)     # flask_sqlalchemy
scheduler = flask_apscheduler.APScheduler()             # flask_apscheduler
login_manager = flask_login.LoginManager()              # flask_login
bcrypt = flask_bcrypt.Bcrypt()                          # flask_bcrypt
redis_store = flask_redis.Redis()                       # flask_redis

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

def create_app(config_name):
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    if os.path.isfile(os.path.join(app.instance_path, "logging.cfg")):
        # app.config.from_pyfile("logging.cfg")
        with app.open_instance_resource("logging.cfg", "r") as json_file:
            logging.config.dictConfig(json.load(json_file))
    # if "LOGGING_CONFIG" in os.environ:
    #     logging.config.dictConfig(json.loads(os.environ["LOGGING_CONFIG"]))

    db.init_app(app)
    app.db = db
    config[config_name].init_app(app)
    scheduler.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    if app.config["REDIS_PASSWORD"]:
        redis_store.init_app(app)
    if config_name != "testing":
        scheduler.start()
        app.logger.info("Scheduler Started")

    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix="/admin")

    from .routes.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/api")

    from .routes.channel import channel as channel_blueprint
    app.register_blueprint(channel_blueprint, url_prefix="/channel")

    from .routes.dev import dev as dev_blueprint
    app.register_blueprint(dev_blueprint, url_prefix="/dev")

    from .routes.user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix="/user")

    from .views import route_blueprint
    app.register_blueprint(route_blueprint)

    from .handler import handler
    app.register_blueprint(handler)

    return app
