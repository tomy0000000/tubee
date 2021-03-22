"""Test Cases of Celery Tasks"""
import unittest
from unittest import mock

from tubee import create_app, db
from tubee.tasks import channels_fetch_videos, channels_refresh, renew_channels


class BasicsTestCase(unittest.TestCase):
    """Test Cases of App Basics"""

    def setUp(self):
        self.app = create_app("testing")
        self.app.config["SERVER_NAME"] = "test_host"
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        self.test_channel_ids = [
            "UCBR8-60-B28hp2BmDPdntcQ",
            "UCpd0xtuhhWwUug1bk84usiA",
            "UCnIQPPwWpO_EFEqLny6TFTw",
            "UCL8ZULXASCc1I_oaOT0NaOQ",
        ]

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @mock.patch("tubee.tasks.channels_refresh")
    @mock.patch("tubee.tasks.Channel")
    def test_tasks_renew_channels(self, mocked_channel, mocked_channels_refresh):
        mocked_channel.query.get.return_value = False
        renew_channels(self.test_channel_ids)

        mocked_channel.query.get.return_value = mock.MagicMock()
        renew_channels(self.test_channel_ids)

    @mock.patch("tubee.tasks.Channel")
    def test_channels_refresh(self, mocked_channel):

        mocked_channel.query.get.return_value = False
        channels_refresh(self.test_channel_ids)

        mocked_channel.query.get.return_value = mock.MagicMock()
        channels_refresh(self.test_channel_ids)

    @mock.patch("tubee.tasks.Channel")
    def test_channels_fetch_videos(self, mocked_channel):
        mocked_channel.query.get.return_value = False
        channels_fetch_videos(self.test_channel_ids)

        mocked_channel.query.get.return_value = mock.MagicMock()
        channels_fetch_videos(self.test_channel_ids)
