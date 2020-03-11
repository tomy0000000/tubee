"""Main Application of Tubee"""
import json
import logging.config
import os
from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import current_user, LoginManager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from config import config

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=naming_convention)
db = SQLAlchemy(metadata=metadata)
bcrypt = Bcrypt()
login_manager = LoginManager()
moment = Moment()
oauth = OAuth()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    if os.path.isfile(os.path.join(app.instance_path, "logging.cfg")):
        with app.open_instance_resource("logging.cfg", "r") as json_file:
            logging.config.dictConfig(json.load(json_file))
            app.logger.info("External logging.cfg Loaded")

    db.init_app(app)
    app.db = db
    config[config_name].init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    oauth.init_app(app)

    login_manager.login_view = "user.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    oauth.register(name="LineNotify",
                   access_token_url="https://notify-bot.line.me/oauth/token",
                   access_token_params=None,
                   authorize_url="https://notify-bot.line.me/oauth/authorize",
                   authorize_params=dict(response_type="code", scope="notify"),
                   api_base_url="https://notify-api.line.me/",
                   client_kwargs=None,
                   fetch_token=lambda: dict(access_token=current_user.
                                            line_notify_credentials,
                                            token_type="bearer"))

    from .routes.main import main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes.admin import admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix="/admin")

    from .routes.api import api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/api")

    from .routes.channel import channel_blueprint
    app.register_blueprint(channel_blueprint, url_prefix="/channel")

    from .routes.user import user_blueprint
    app.register_blueprint(user_blueprint, url_prefix="/user")

    if app.debug:
        from .routes.dev import dev_blueprint
        app.register_blueprint(dev_blueprint, url_prefix="/dev")
    else:
        from .handler import handler
        app.register_blueprint(handler)

    return app
