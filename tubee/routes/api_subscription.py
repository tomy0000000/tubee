from flask import Blueprint, get_template_attribute, jsonify, request, session
from flask_login import current_user, login_required

api_subscription_blueprint = Blueprint("api_subscription", __name__)


@api_subscription_blueprint.post("/")
@login_required
def create():
    """Add Subscription"""
    channel_id = request.get_json().get("channel_id")
    response = current_user.subscribe(channel_id)
    return jsonify(response)


@api_subscription_blueprint.delete("/")
@login_required
def delete():
    """Remove subscription"""
    channel_id = request.get_json().get("channel_id")
    response = current_user.unbsubscribe(channel_id)
    return jsonify(response)


@api_subscription_blueprint.post("/tag")
@login_required
def tag_create():
    """Add a tag to subscription"""
    data = request.get_json()
    channel_id = data.get("channel_id")
    tag_name = data.get("tag_name")

    subscription = current_user.subscriptions.filter_by(
        channel_id=channel_id
    ).first_or_404()
    response = subscription.tag(tag_name)
    return jsonify(response)


@api_subscription_blueprint.delete("/tag")
@login_required
def tag_delete():
    """Remove a tag from subscription"""
    data = request.get_json()
    channel_id = data.get("channel_id")
    tag_id = data.get("tag_id")

    subscription = current_user.subscriptions.filter_by(
        channel_id=channel_id
    ).first_or_404("Channel not found")
    response = subscription.untag(tag_id)
    return jsonify(response)


@api_subscription_blueprint.get("/youtube")
@login_required
def youtube():
    """Load YouTube Subscription"""
    draw = int(request.args.get("draw"))
    start = int(request.args.get("start"))
    length = int(request.args.get("length"))
    page = int(start / length) + 1

    previous_page = session.get("youtube_page")
    previous_length = session.get("youtube_page_length")

    page_token = None
    if length == previous_length:
        if page > previous_page:
            page_token = session.get("youtube_next_token")
        else:
            page_token = session.get("youtube_prev_token")

    query = (
        current_user.youtube.subscriptions()
        .list(
            part="snippet",
            maxResults=length,
            mine=True,
            order="alphabetical",
            pageToken=page_token,
        )
        .execute()
    )
    for channel in query["items"]:
        channel_id = channel["snippet"]["resourceId"]["channelId"]
        channel["snippet"]["subscribed"] = current_user.is_subscribing(channel_id)
    count = query["pageInfo"]["totalResults"]
    response = {
        "datatable": True,
        "draw": draw,
        "recordsTotal": count,
        "recordsFiltered": count,
        "data": [
            [
                get_template_attribute(
                    "macros/subscription.html", "youtube_table_thumbnail"
                )(channel),
                get_template_attribute(
                    "macros/subscription.html", "youtube_table_info"
                )(channel),
                get_template_attribute(
                    "macros/subscription.html", "youtube_table_button"
                )(channel),
            ]
            for channel in query["items"]
        ],
    }
    session["youtube_page"] = page
    session["youtube_page_length"] = length
    session["youtube_prev_token"] = query.get("prevPageToken")
    session["youtube_next_token"] = query.get("nextPageToken")
    return response
