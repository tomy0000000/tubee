"""Test Cases of Video Model"""
import unittest
from unittest import mock

from tubee import create_app, db
from tubee.models import Channel, Video


class UserModelTestCase(unittest.TestCase):
    """Test Cases of User Model"""

    def setUp(self):
        self.app = create_app("testing")
        self.app.config["SERVER_NAME"] = "test_host"
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.test_channel_id = "UCBR8-60-B28hp2BmDPdntcQ"
        self.test_video_id = ["9GCTgqi66nI", "CDhN71SLcZ8"]

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @mock.patch("tubee.models.channel.Channel.activate")
    @mock.patch("tubee.tasks.channels_renew")
    @mock.patch("tubee.tasks.channels_fetch_videos")
    @mock.patch("tubee.tasks.channels_refresh")
    @mock.patch("tubee.models.channel.Channel.update")
    def init_channel(
        self,
        mocked_update,
        mocked_channels_refresh,
        mocked_channels_fetch_videos,
        mocked_channels_renew,
        mocked_activate,
    ):
        mocked_update.return_value = True
        mocked_channels_refresh.apply_async.return_value = None
        mocked_channels_fetch_videos.apply_async.return_value = None
        mocked_activate.return_value = None
        self.test_channel = Channel(channel_id=self.test_channel_id)

    @mock.patch("tubee.models.video.Video.update_infos")
    def test_video_constructor(self, mocked_update_infos):
        self.init_channel()
        self.test_video = Video(self.test_video_id[0], self.test_channel)
        self.test_video = Video(
            self.test_video_id[1], self.test_channel, fetch_infos=False
        )
