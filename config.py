import logging
import os
import uuid
from datetime import timedelta

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
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE = True

    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")

    YOUTUBE_API_DEVELOPER_KEY = os.environ.get("YOUTUBE_API_DEVELOPER_KEY")
    PUSHOVER_TOKEN = os.environ.get("PUSHOVER_TOKEN")

    # YouTube Data API
    YOUTUBE_API_CLIENT_SECRET_FILE = os.environ.get("YOUTUBE_API_CLIENT_SECRET_FILE")
    YOUTUBE_READ_WRITE_SSL_SCOPE = ["https://www.googleapis.com/auth/youtube.force-ssl"]
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
        pass


class DevelopmentConfig(Config):
    """Config for local Development"""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        app.logger.setLevel(logging.DEBUG)
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


class TestingConfig(Config):
    """Config for Testing, Travis CI"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite://")
    WTF_CSRF_ENABLED = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "data.sqlite")
    DEPLOY_KEY = os.environ.get("DEPLOY_KEY")

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        app.logger.setLevel(logging.INFO)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to syslog
        from logging.handlers import SysLogHandler

        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.INFO)
        logging.addHandler(syslog_handler)


class DockerConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        logging.info("Docker Config Loaded")


class HerokuConfig(ProductionConfig):
    SSL_REDIRECT = bool(os.environ.get("DYNO"))

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # handle reverse proxy server headers
        from werkzeug.contrib.fixers import ProxyFix

        app.wsgi_app = ProxyFix(app.wsgi_app)

        # log to stderr
        logging.info("Heroku Config Loaded")


class GoogleCloudAppEngineConfig(ProductionConfig):

    GOOGLE_CLOUD_PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT_ID")
    GOOGLE_CLOUD_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION")
    GOOGLE_CLOUD_TASK_QUEUE = os.environ.get("GOOGLE_CLOUD_TASK_QUEUE")

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log from stderr will be redirected to stackdriver
        import google.cloud.logging

        client = google.cloud.logging.Client()
        client.setup_logging()
        logging.info("App Engine Config Loaded")


class GoogleCloudComputeEngineConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stackdriver
        import google.cloud.logging

        client = google.cloud.logging.Client()
        client.setup_logging()
        logging.info("Compute Engine Config Loaded")


config = {
    "default": DevelopmentConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "unix": UnixConfig,
    "docker": DockerConfig,
    "heroku": HerokuConfig,
    "gae": GoogleCloudAppEngineConfig,
    "gce": GoogleCloudComputeEngineConfig,
}
