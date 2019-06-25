"""Function to be executed by Scheduler"""
import random
from datetime import datetime, timedelta
from ..models import User
from .. import db, scheduler

def test_func():
    print("Hello World")

def renew_channel(channel):
    """Trigger Renew Function of Channel"""
    print("Auto Renew Function Triggered!!!")
    print("Running Renew for Channel: {}".format(channel.channel_name))

    # Main
    with db.app.app_context():
        infos = channel.renew()
    renew_datetime = infos["expiration"] - timedelta(days=1)

    # Main (beta)
    # random_num = random.randint(0, 30)
    # infos = {"expiration": "Testing, no Expiration"}
    # renew_datetime = datetime.now() + timedelta(seconds=random_num)

    # Beta Procedure
    admins = User.query.filter_by(admin=True).all()
    for admin in admins:
        admin.send_notification("Channel Renew",
                                ("Channel Name: {}\n"+\
                                 "Channel ID: {}\n"+\
                                 "New Expiration: {}\n"+\
                                 "Renew Scheduled at: {}").format(
                                     channel.channel_name,
                                     channel.channel_id,
                                     infos["expiration"],
                                     renew_datetime),
                                title="Channel Auto Renewed")

    # Schedule for Next Run
    print("next run is scheduled at {}".format(renew_datetime))
    response = scheduler.add_job(id="renew_channel_{}".format(channel.channel_name),
                                 func=renew_channel,
                                 args=[channel],
                                 run_date=renew_datetime)
