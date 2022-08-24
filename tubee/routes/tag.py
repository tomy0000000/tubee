from datetime import datetime, timedelta

from flask import Blueprint, current_app, render_template, request
from flask_login import current_user, login_required

from .. import db
from ..models import Channel, Subscription, SubscriptionTag, Tag, Video, VideoCheck

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


@tag_blueprint.get("/<tag_id>/videos")
@login_required
def videos(tag_id: int):
    """Showing videos from subscribed channels with specified tag"""

    # Check if provided tag exists
    Tag.query.get_or_404(tag_id, "Tag not found")

    # Filter subscritions by tag, including tag or untagged
    last_30_days = datetime.utcnow() - timedelta(days=30)
    queried_row = (
        db.session.query(Subscription, SubscriptionTag, Video, VideoCheck)
        .outerjoin(SubscriptionTag)
        .outerjoin(Video, Subscription.channel_id == Video.channel_id)
        .outerjoin(VideoCheck, VideoCheck.video_id == Video.id)
        .where(SubscriptionTag.tag_id == tag_id)
        .where(Video.uploaded_timestamp > last_30_days)
        .where(VideoCheck.checked.is_(None) | VideoCheck.checked.is_(False))
        .all()
    )
    video_ids = [row["Video"].id for row in queried_row]
    return render_template("tag/videos.html", rows=queried_row, video_ids=video_ids)
