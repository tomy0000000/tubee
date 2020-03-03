import os
import uuid
from datetime import timedelta
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Universal Config"""
    DEBUG = False
    TESTING = False
    PREFERRED_URL_SCHEME = "https"
    SERVER_NAME = os.environ.get("SERVER_NAME")
    APPLICATION_ROOT = os.environ.get("APPLICATION_ROOT", "/")
    SECRET_KEY = os.environ.get("SECRET_KEY", str(uuid.uuid4()))
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_recycle": 300}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CUSTOM_SQLALCHEMY_NAMEING_CONVENTIONS = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE = True

    YOUTUBE_API_DEVELOPER_KEY = os.environ.get("YOUTUBE_API_DEVELOPER_KEY")
    PUSHOVER_TOKEN = os.environ.get("PUSHOVER_TOKEN")

    # YouTube Data API
    YOUTUBE_API_CLIENT_SECRET_FILE = os.environ.get(
        "YOUTUBE_API_CLIENT_SECRET_FILE")
    YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    # Line Notify API
    LINENOTIFY_CLIENT_ID = os.environ.get("LINENOTIFY_CLIENT_ID")
    LINENOTIFY_CLIENT_SECRET = os.environ.get("LINENOTIFY_CLIENT_SECRET")

    # Dropbox API
    DROPBOX_APP_KEY = os.environ.get("DROPBOX_APP_KEY")
    DROPBOX_APP_SECRET = os.environ.get("DROPBOX_APP_SECRET")

    # PubSubHubBub
    HUB_GOOGLE_HUB = "https://pubsubhubbub.appspot.com"
    HUB_YOUTUBE_TOPIC = "https://www.youtube.com/xml/feeds/videos.xml?"
    HUB_RECEIVE_DOMAIN = os.environ.get("HUB_RECEIVE_DOMAIN", SERVER_NAME)

    @staticmethod
    def init_app(app):
        with app.app_context():
            app.config["SCHEDULER_JOBSTORES"] = {
                "default": SQLAlchemyJobStore(engine=app.db.engine)
            }


class DevelopmentConfig(Config):
    """Config for local Development"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


class TestingConfig(Config):
    """Config for Testing, Travis CI"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or \
        "sqlite://"
    WTF_CSRF_ENABLED = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "data.sqlite")
    DEPLOY_KEY = os.environ.get("DEPLOY_KEY")

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.INFO)
        app.logger.addHandler(syslog_handler)


class HerokuConfig(ProductionConfig):
    SSL_REDIRECT = bool(os.environ.get("DYNO"))

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # handle reverse proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


class GoogleCloudAppEngineConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # logs from stderr will be redirected to stackdriver
        import logging
        from logging import StreamHandler
        app.logger.addHandler(StreamHandler())
        app.logger.setLevel(logging.INFO)
        app.logger.info("App Engine Config Loaded")


class GoogleCloudComputeEngineConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stackdriver
        import google.cloud.logging
        client = google.cloud.logging.Client()
        client.setup_logging()


config = {
    "default": DevelopmentConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "unix": UnixConfig,
    "heroku": HerokuConfig,
    "gae": GoogleCloudAppEngineConfig,
    "gce": GoogleCloudComputeEngineConfig,
    # "docker": DockerConfig,
}
