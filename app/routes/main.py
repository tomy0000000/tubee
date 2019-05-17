"""The Main Routes"""
from flask import Blueprint, render_template
from flask_login import login_required
from ..models import Channel
main = Blueprint("main", __name__)

@main.route("/")
@login_required
def dashboard(alert="", alert_type=""):
    """Showing All Subscribed Channels"""
    channels = Channel.query.order_by(Channel.channel_name).all()
    return render_template("dashboard.html",
                           subscriptions=channels,
                           alert=alert,
                           alert_type=alert_type)
