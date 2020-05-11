"""Main Application of Tubee"""
import json
import logging.config
import os

from authlib.integrations.flask_client import OAuth
from celery import Celery
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from config import Config, config

__version__ = "dev"

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


metadata = MetaData(naming_convention=naming_convention)
db = SQLAlchemy(metadata=metadata)
bcrypt = Bcrypt()
login_manager = LoginManager()
moment = Moment()
oauth = OAuth()
celery = Celery(__name__)


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    if os.path.isfile(os.path.join(app.instance_path, "logging.cfg")):
        with app.open_instance_resource("logging.cfg", "r") as json_file:
            logging.config.dictConfig(json.load(json_file))
            logging.info("External logging.cfg Loaded")

    db.init_app(app)
    app.db = db
    config[config_name].init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    oauth.init_app(app)
    celery.conf.update(app.config)

    login_manager.login_view = "user.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    login_manager.needs_refresh_message = "Please reauthenticate to access this page."
    login_manager.needs_refresh_message_category = "warning"
    oauth.register(
        name="LineNotify",
        access_token_url="https://notify-bot.line.me/oauth/token",
        access_token_params=None,
        authorize_url="https://notify-bot.line.me/oauth/authorize",
        authorize_params=dict(response_type="code", scope="notify"),
        api_base_url="https://notify-api.line.me/",
        client_kwargs=None,
        fetch_token=lambda: dict(
            access_token=current_user._line_notify_credentials, token_type="bearer"
        ),
    )

    # from .routes.app_engine import app_engine_blueprint
    from .routes.admin import admin_blueprint
    from .routes.api import api_blueprint
    from .routes.channel import channel_blueprint
    from .routes.dev import dev_blueprint
    from .routes.main import main_blueprint
    from .routes.user import user_blueprint
    from .handler import handler

    app.register_blueprint(main_blueprint)
    app.register_blueprint(admin_blueprint, url_prefix="/admin")
    app.register_blueprint(api_blueprint, url_prefix="/api")
    app.register_blueprint(channel_blueprint, url_prefix="/channel")
    app.register_blueprint(user_blueprint, url_prefix="/user")
    # if app.config["GOOGLE_CLOUD_PROJECT_ID"]:
    #     app.register_blueprint(app_engine_blueprint, url_prefix="/app_engine")
    if app.debug:
        app.register_blueprint(dev_blueprint, url_prefix="/dev")
        # else:
        app.register_blueprint(handler)

    return app
