from .admin import admin_blueprint
from .api import api_blueprint
from .api_action import api_action_blueprint
from .api_channel import api_channel_blueprint
from .api_tag import api_tag_blueprint
from .api_task import api_task_blueprint
from .dev import dev_blueprint
from .handler import handler_blueprint
from .main import main_blueprint
from .user import user_blueprint

blueprint_map = [
    ("", handler_blueprint),
    ("", main_blueprint),
    ("/admin", admin_blueprint),
    ("/api", api_blueprint),
    ("/api/action", api_action_blueprint),
    ("/api/channel", api_channel_blueprint),
    ("/api/tag", api_tag_blueprint),
    ("/api/task", api_task_blueprint),
    ("/dev", dev_blueprint),
    ("/user", user_blueprint),
]

__all__ = [
    admin_blueprint,
    api_blueprint,
    api_action_blueprint,
    api_channel_blueprint,
    api_tag_blueprint,
    api_task_blueprint,
    blueprint_map,
    dev_blueprint,
    handler_blueprint,
    main_blueprint,
    user_blueprint,
]
