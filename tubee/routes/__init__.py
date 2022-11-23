from .action import action_blueprint
from .admin import admin_blueprint
from .api import api_blueprint
from .api_action import api_action_blueprint
from .api_admin import api_admin_blueprint
from .api_channel import api_channel_blueprint
from .api_subscription import api_subscription_blueprint
from .api_tag import api_tag_blueprint
from .api_task import api_task_blueprint
from .api_video import api_video_blueprint
from .main import main_blueprint
from .tag import tag_blueprint
from .user import user_blueprint

__all__ = [
    "action_blueprint",
    "admin_blueprint",
    "api_blueprint",
    "api_action_blueprint",
    "api_admin_blueprint",
    "api_channel_blueprint",
    "api_subscription_blueprint",
    "api_tag_blueprint",
    "api_task_blueprint",
    "api_video_blueprint",
    "blueprint_map",
    "main_blueprint",
    "tag_blueprint",
    "user_blueprint",
]

blueprint_map = [
    ("/action", action_blueprint),
    ("/admin", admin_blueprint),
    ("/api", api_blueprint),
    ("/api/action", api_action_blueprint),
    ("/api/admin", api_admin_blueprint),
    ("/api/channel", api_channel_blueprint),
    ("/api/subscription", api_subscription_blueprint),
    ("/api/tag", api_tag_blueprint),
    ("/api/task", api_task_blueprint),
    ("/api/video", api_video_blueprint),
    ("", main_blueprint),
    ("/tag", tag_blueprint),
    ("/user", user_blueprint),
]
