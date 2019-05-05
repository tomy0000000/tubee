"""Main Application of Tubee"""
import atexit
import codecs
import flask
import flask_apscheduler
import flask_bcrypt
import flask_login
import flask_redis
import flask_sqlalchemy
import logging.config
import os
import sys
from config import config

db = flask_sqlalchemy.SQLAlchemy()              # flask_sqlalchemy
scheduler = flask_apscheduler.APScheduler()     # flask_apscheduler
login_manager = flask_login.LoginManager()      # flask_login
bcrypt = flask_bcrypt.Bcrypt()                  # flask_bcrypt
redis_store = flask_redis.Redis()               # flask_redis

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

    if issubclass(config[config_name], config["production"]):
        app.logger.info(config_name+" build log production")
        print(config_name+" build log production")
        app.config["LOADED_CONFIG"] = "production"
    else:
        app.logger.info(config_name+" build log "+config_name)
        print(config_name+" build log "+config_name)
        app.config["LOADED_CONFIG"] = config_name
    if "LOGGING_CONFIG" in app.config:
        logging.config.dictConfig(app.config["LOGGING_CONFIG"])

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

    from .routes.dev import dev as dev_blueprint
    app.register_blueprint(dev_blueprint, url_prefix="/dev")

    from .routes.login import login as login_blueprint
    app.register_blueprint(login_blueprint, url_prefix="/login")

    from .views import route_blueprint
    app.register_blueprint(route_blueprint)

    from .handler import handler_blueprint
    app.register_blueprint(handler_blueprint)

    return app
