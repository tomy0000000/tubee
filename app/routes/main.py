"""The Main Routes"""
from flask import Blueprint, render_template
from flask_login import current_user, login_required
from ..models import Subscription
main = Blueprint("main", __name__)

@main.route("/")
@login_required
def dashboard():
    """Showing All Subscribed Channels"""
    subscriptions = Subscription.query.order_by(Subscription.channel_name).all()
    return render_template("dashboard.html", subscriptions=subscriptions)

@main.context_processor
def inject_username():
    if current_user.is_anonymous:
        username = "Guest"
    else:
        username = current_user.username
    return dict(username=username)
