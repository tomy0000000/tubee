from flask import Blueprint, render_template
from flask_login import current_user  # type: ignore
from flask_login import login_required

from ..models import Tag, User

current_user: User

tag_blueprint = Blueprint("tag", __name__)


@tag_blueprint.get("/")
@login_required
def listing():
    tags = current_user.tags.order_by(Tag.sort_index.asc()).all()
    subscriptions = current_user.subscriptions.all()
    return render_template("tag/listing.html", tags=tags, subscriptions=subscriptions)


@tag_blueprint.get("/<tag_id>")
@login_required
def main(tag_id: int):
    """Showing Subscribed Channels with specified tag"""
    tag = Tag.query.get_or_404(tag_id, "Tag not found")
    actions = current_user.actions.join(Tag).filter(Tag.id == tag_id).all()
    return render_template("tag/main.html", tag=tag, actions=actions)
