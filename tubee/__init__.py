"""Main Application of Tubee"""
import json
import logging.config
import os
import flask
from authlib.flask.client import OAuth
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_moment import Moment
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
bcrypt = Bcrypt()                                           # flask_bcrypt
login_manager = LoginManager()                              # flask_login
moment = Moment()                                           # flask_moment
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
    bcrypt.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)

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
