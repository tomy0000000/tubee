import os
import uuid
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base Config"""

    DEBUG = False
    TESTING = False
    PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME", "https")
    SERVER_NAME = os.environ.get("SERVER_NAME")
    APPLICATION_ROOT = os.environ.get("APPLICATION_ROOT", "/")
    SECRET_KEY = os.environ.get("SECRET_KEY", str(uuid.uuid4()))
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_recycle": 300}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_NAMING_CONVENTION = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE = True

    # Celery
    BROKER_URL = os.environ.get(
        "BROKER_URL", "amqp://guest:guest@tubee_rabbitmq:5672//"
    )

    # Sentry
    SENTRY_DSN = os.environ.get("SENTRY_DSN")

    # Pushover
    PUSHOVER_TOKEN = os.environ.get("PUSHOVER_TOKEN")

    # YouTube Data API
    YOUTUBE_API_DEVELOPER_KEY = os.environ.get("YOUTUBE_API_DEVELOPER_KEY")
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

    @staticmethod
    def init_app(app):
        app.db.metadata.naming_convention = app.config["SQLALCHEMY_NAMING_CONVENTION"]


class DevelopmentConfig(Config):
    """Config for local Development"""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'data.sqlite')}"
    )

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


class TestingConfig(Config):
    """Config for Testing"""

    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite://")

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
