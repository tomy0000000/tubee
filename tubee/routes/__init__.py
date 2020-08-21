from .admin import admin_blueprint
from .api import api_blueprint
from .channel import channel_blueprint
from .dev import dev_blueprint
from .handler import handler_blueprint
from .main import main_blueprint
from .user import user_blueprint

blueprint_map = [
    ("", handler_blueprint),
    ("", main_blueprint),
    ("/admin", admin_blueprint),
    ("/api", api_blueprint),
    ("/channel", channel_blueprint),
    ("/dev", dev_blueprint),
    ("/user", user_blueprint),
]

__all__ = [
    admin_blueprint,
    api_blueprint,
    blueprint_map,
    channel_blueprint,
    dev_blueprint,
    handler_blueprint,
    main_blueprint,
    user_blueprint,
]
