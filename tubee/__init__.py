"""Main Application of Tubee"""
from typing import Union

import sentry_sdk
from authlib.integrations.flask_client import OAuth
from celery import Celery
from coverage import Coverage
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from jinja2 import StrictUndefined
from loguru import logger
from sentry_sdk.integrations.flask import FlaskIntegration

from tubee.config import config

VERSION = "0.13.0"

db = SQLAlchemy()
bcrypt = Bcrypt()
celery = Celery(__name__)
login_manager = LoginManager()
migrate = Migrate()
oauth = OAuth()


class Tubee(Flask):
    def __init__(
        self, *args, db: SQLAlchemy, coverage: Union[Coverage, None] = None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.version = VERSION
        self.db = db
        self.coverage = coverage


def create_app(config_name="development", coverage=None) -> Tubee:
    from .utils import PropagateToGunicorn, get_line_notify_fetch_token

    # App Fundation
    app = Tubee(__name__, db=db, coverage=coverage, instance_relative_config=True)

    # Config settings
    config_instance = config[config_name]
    app.config.from_object(config_instance)

    # Extensions Initialization
    db.init_app(app)
    config_instance.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    oauth.init_app(app)
    celery.conf.update(
        broker_url="amqp://guest:guest@tubee_rabbitmq:5672//", result_backend="rpc://"
    )

    # Register Sentry
    if not app.debug and config_instance.SENTRY_DSN:
        sentry_sdk.init(
            dsn=config_instance.SENTRY_DSN,
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.2,
            release=VERSION,
        )

    # Setup loguru
    logger.add("tubee.log", level="INFO", rotation="25 MB")
    logger.add(PropagateToGunicorn(), colorize=True)

    # Extensions Settings
    login_manager.login_view = "user.login"  # type: ignore
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
        fetch_token=get_line_notify_fetch_token,
    )

    from .routes import blueprint_map
    from .utils import commands, processor

    for command in commands.__all__:
        app.cli.add_command(getattr(commands, command))

    for prefix, blueprint in blueprint_map:
        if prefix.startswith("/api"):
            blueprint.after_request(processor.api_formatter)
        app.register_blueprint(blueprint, url_prefix=prefix)

    if app.debug:
        app.jinja_env.undefined = StrictUndefined
    else:
        app.register_error_handler(Exception, processor.error_handler)  # Error handler
    app.context_processor(processor.template)  # Variables for jinja templates
    app.shell_context_processor(processor.shell)  # Variables for shell

    return app
