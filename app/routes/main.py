"""The Main Routes"""
from datetime import datetime
from flask import Blueprint, current_app, render_template, request
from flask_login import current_user, login_required
from .. import db
from ..models import Subscription
main = Blueprint("main", __name__)

@main.context_processor
def inject_username():
    if current_user.is_anonymous:
        username = "Guest"
    else:
        username = current_user.username
    return dict(username=username)

@main.route("/")
@login_required
def dashboard(alert="", alert_type=""):
    """Showing All Subscribed Channels"""
    subscriptions = Subscription.query.order_by(Subscription.channel_name).all()
    return render_template("dashboard.html",
                           subscriptions=subscriptions,
                           alert=alert,
                           alert_type=alert_type)