from flask import Blueprint, current_app, render_template, request
from flask_login import current_user, login_required

from ..models import Channel, SubscriptionTag, Tag

tag_blueprint = Blueprint("tag", __name__)


@tag_blueprint.route("/")
@login_required
def listing():
    tags = current_user.tags.all()
    return render_template("tag/listing.html", tags=tags)


@tag_blueprint.route("/<tag_id>")
@login_required
def main(tag_id: int):
    """Showing Subscribed Channels with specified tag"""

    # Check if provided tag exists
    tag = Tag.query.get_or_404(tag_id, "Tag not found")

    # Filter subscritions by tag, including tag or untagged
    subscriptions = (
        current_user.subscriptions.outerjoin(Channel)
        .outerjoin(SubscriptionTag)
        .outerjoin(Tag)
        .filter(Tag.id == tag_id)
        .order_by(Channel.name.asc())
    )
    actions = current_user.actions.join(Tag).filter(Tag.id == tag_id).all()

    # Paginate subscriptions
    page = request.args.get("page", 1, type=int)
    pagination = subscriptions.paginate(
        page, current_app.config["PAGINATE_COUNT"], False
    )
    return render_template(
        "tag/main.html",
        subscription_pagination=pagination,
        tag=tag,
        actions=actions,
    )
