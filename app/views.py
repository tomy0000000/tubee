"""Views for Tubee"""
from flask import render_template
from . import scheduler
from .models import Channel
from .routes.main import main_blueprint

@main_blueprint.route("/hub/status")
def hub_status():
    channels = Channel.query.order_by(Channel.channel_name).all()
    return render_template("status.html", channels=channels)

@main_blueprint.route("/hub/renew")
def hub_renew():
    response = {}
    for channel in Channel.query.filter(Channel.active):
        response[channel.channel_id] = channel.renew_hub()
    return render_template("empty.html", info=response)

def test_func():
    print("Hello")

@main_blueprint.route("/regist_job")
def reg_job():
    response = scheduler.add_job("test", test_func, trigger="interval", seconds=2)
    return render_template("empty.html", info=response)
