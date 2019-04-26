import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Universal Config"""
    SECRET_KEY = os.environ.get("SECRET_KEY") or "aef142c0-b8d5-4ad2-bbbc-d4b101adcd05"
    PREFERRED_URL_SCHEME = "https"
    SQLALCHEMY_POOL_RECYCLE = 480
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None
    REDIS_HOST = os.environ.get("REDIS_HOST") or None
    REDIS_PORT = os.environ.get("REDIS_PORT") or None
    REDIS_DB = os.environ.get("REDIS_DB") or None
    YOUTUBE_API_DEVELOPER_KEY = os.environ.get("YOUTUBE_API_DEVELOPER_KEY")
    PUSHOVER_TOKEN = os.environ.get("PUSHOVER_TOKEN")

    # YouTube Data API
    YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    # PubSubHubBub
    HUB_GOOGLE_HUB = "https://pubsubhubbub.appspot.com"
    HUB_YOUTUBE_TOPIC = "https://www.youtube.com/xml/feeds/videos.xml?"

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Config for local Development"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")
    # SCHEDULER_JOBSTORES = {
    #     "default": {
    #         "type": "sqlalchemy",
    #         "url": SQLALCHEMY_DATABASE_URI
    #     }
    # }

class TestingConfig(Config):
    """Config for Testing, Travis CI"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or \
        "sqlite://"
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "data.sqlite")

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

config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "heroku": HerokuConfig,
    # "docker": DockerConfig,
    "unix": UnixConfig,
    "default": DevelopmentConfig
}
