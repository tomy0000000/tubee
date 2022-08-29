"""Test Cases of Channel Model"""
import json
import unittest
from datetime import datetime, timezone
from os.path import dirname, join
from unittest import mock

from googleapiclient.discovery import build
from googleapiclient.errors import Error as YouTubeAPIError
from googleapiclient.http import HttpMockSequence

from tubee import create_app, db
from tubee.exceptions import APIError, InvalidAction
from tubee.models import Channel


class ChannelModelTestCase(unittest.TestCase):
    """Test Cases of Channel Model"""

    def setUp(self):
        self.app = create_app("testing")
        self.app.config["SERVER_NAME"] = "test_host"
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.test_channel_id = "UCBR8-60-B28hp2BmDPdntcQ"
        self.test_username = "test_user"
        self.test_user_password = "test_password"
        self.test_pushover_key = "test_pushover"

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

    @mock.patch("tubee.tasks.channels_renew")
    @mock.patch("tubee.tasks.channels_fetch_videos")
    @mock.patch("tubee.tasks.channels_refresh")
    @mock.patch("tubee.models.channel.Channel.update")
    def test_channel_constructor(
        self,
        mocked_update,
        mocked_channels_refresh,
        mocked_channels_fetch_videos,
        mocked_channels_renew,
    ):
        mocked_update.side_effect = InvalidAction("test_message")
        with self.assertRaises(InvalidAction):
            Channel(channel_id=self.test_channel_id)

        mocked_update.side_effect = None
        self.init_channel()
        for call in mocked_channels_refresh.apply_async.call_args_list:
            args, kwargs = call
            self.assertEqual(len(kwargs["args"]), 1)
            self.assertIsInstance(kwargs["args"][0], list)
            self.assertIsInstance(kwargs["args"][0][0], tuple)
            self.assertEqual(kwargs["args"][0][0][0], self.test_channel_id)
            self.assertTrue(kwargs["args"][0][0][1].startswith("http"))
            self.assertIn(self.test_channel_id, kwargs["args"][0][0][1])
            self.assertIn(self.test_channel_id, kwargs["args"][0][0][2])
        for call in mocked_channels_fetch_videos.apply_async.call_args_list:
            args, kwargs = call
            self.assertEqual(kwargs["args"][0][0], self.test_channel_id)
        for call in mocked_channels_renew.apply_async.call_args_list:
            args, kwargs = call
            self.assertEqual(kwargs["args"][0][0][0], self.test_channel_id)
            self.assertTrue(kwargs["args"][0][0][1].startswith("http"))
            self.assertIn(self.test_channel_id, kwargs["args"][0][0][1])
            self.assertIn(self.test_channel_id, kwargs["args"][0][0][2])
        self.assertEqual(self.test_channel.id, self.test_channel_id)

    def test_channel_expiration_getter(self):
        self.init_channel()
        self.test_channel.hub_infos = {"expiration": str(datetime.now())}
        self.assertIsNotNone(self.test_channel.expiration)

    def test_channel_expiration_setter(self):
        self.init_channel()
        with self.assertRaises(ValueError):
            self.test_channel.expiration = datetime.now()

    def test_channel_expiration_deleter(self):
        self.init_channel()
        with self.assertRaises(ValueError):
            del self.test_channel.expiration

    @mock.patch("tubee.models.channel.details")
    def test_channel_refresh(
        self,
        mocked_hub_details,
    ):
        self.init_channel()
        self.test_channel.hub_infos = {
            "state": "verified",
            "stat": "0 delivery request(s) per second to localhost,\n      0% errors",
            "last_challenge": None,
            "expiration": None,
            "last_subscribe": "2020-01-01 10:30:00+00:00",
            "last_unsubscribe": None,
            "last_challenge_error": [
                "2020-01-01 10:30:00+00:00",
                "Bad response code 504",
            ],
            "last_notification_error": None,
            "last_notification": None,
        }
        mocked_hub_details.return_value = {
            "requests_url": "https://pubsubhubbub.appspot.com/subscription-details"
            "?hub.callback=https%3A%2F%2Ftest_host%2Fchannel%2FUCBR8-60-B28hp2BmDPdntcQ"
            "%2Fcallback&hub.topic=https%3A%2F%2Fwww.youtube.com%2Fxml%2Ffeeds"
            "%2Fvideos.xml%3Fchannel_id%3DUCBR8-60-B28hp2BmDPdntcQ",
            "response_object": None,
            "state": "unverified",
            "stat": "0 delivery request(s) per second to localhost,\n      0% errors",
            "last_challenge": datetime(2020, 1, 1, 10, 30, 0, tzinfo=timezone.utc),
            "expiration": datetime(2020, 1, 1, 10, 30, 0, tzinfo=timezone.utc),
            "last_subscribe": datetime(2020, 1, 1, 10, 30, 0, tzinfo=timezone.utc),
            "last_unsubscribe": None,
            "last_challenge_error": (
                datetime(2020, 1, 1, 10, 30, 0, tzinfo=timezone.utc),
                "Bad response code 504",
            ),
            "last_notification_error": (
                datetime(2020, 1, 1, 10, 30, 0, tzinfo=timezone.utc),
                "HTTP 504",
            ),
            "last_notification": datetime(2020, 1, 1, 10, 30, 0, tzinfo=timezone.utc),
        }
        results = self.test_channel.refresh()
        TEST_FIELDS = [
            "last_challenge",
            "expiration",
            "last_subscribe",
            "last_unsubscribe",
            "last_notification",
        ]
        for field in TEST_FIELDS:
            self.assertIsInstance(results[field], (datetime, type(None)))
            self.assertIsInstance(self.test_channel.hub_infos[field], (str, type(None)))
        self.assertIsInstance(results["last_challenge_error"], tuple)
        self.assertIsInstance(self.test_channel.hub_infos["last_challenge_error"], list)
        self.assertIsInstance(results["last_challenge_error"][0], datetime)
        self.assertIsInstance(
            self.test_channel.hub_infos["last_challenge_error"][0], str
        )
        self.assertIsInstance(results["last_notification_error"], tuple)
        self.assertIsInstance(
            self.test_channel.hub_infos["last_notification_error"], list
        )
        self.assertIsInstance(results["last_notification_error"][0], datetime)
        self.assertIsInstance(
            self.test_channel.hub_infos["last_notification_error"][0], str
        )

    @mock.patch("tubee.models.channel.build_youtube_api")
    def test_channel_update(self, mocked_youtube):
        self.init_channel()
        with open(
            join(dirname(__file__), "../data", "youtube_channel_list_empty.json")
        ) as file:
            test_empty_response = json.load(file)
        with open(
            join(dirname(__file__), "../data", "youtube_channel_list.json")
        ) as file:
            test_response = json.load(file)

        mocked_youtube.return_value.channels().list().execute.side_effect = (
            YouTubeAPIError()
        )
        with self.assertRaises(APIError):
            self.test_channel.update()

        mocked_youtube.return_value.channels().list().execute.side_effect = None
        mocked_youtube.return_value.channels().list().execute.return_value = (
            test_empty_response
        )
        with self.assertRaises(InvalidAction):
            self.test_channel.update()
        self.test_channel.name = "test_channel_name"
        with self.assertRaises(APIError):
            self.test_channel.update()

        mocked_youtube.return_value.channels().list().execute.return_value = (
            test_response
        )
        self.test_channel.update()
        self.assertEqual(self.test_channel.infos, test_response["items"][0])
        self.assertEqual(
            self.test_channel.name, test_response["items"][0]["snippet"]["title"]
        )

    @mock.patch("tubee.models.video.Video")
    @mock.patch("tubee.models.channel.build_youtube_api")
    def test_channel_fetch_videos(self, mocked_youtube, mocked_video):
        self.init_channel()

        with open(
            join(dirname(__file__), "../data", "youtube_fetch_videos_1.json")
        ) as file:
            playlist_items_1 = file.read()
        with open(
            join(dirname(__file__), "../data", "youtube_fetch_videos_2.json")
        ) as file:
            playlist_items_2 = file.read()
        responses = [
            ({"status": "200"}, playlist_items_1),
            ({"status": "200"}, playlist_items_2),
        ]

        mocked_youtube.return_value = build(
            self.app.config["YOUTUBE_API_SERVICE_NAME"],
            self.app.config["YOUTUBE_API_VERSION"],
            http=HttpMockSequence(responses),
            developerKey=self.app.config["YOUTUBE_API_DEVELOPER_KEY"],
        )
        mocked_video.query.get.side_effect = lambda x: bool(hash(x) % 2)

        self.test_channel.fetch_videos()

    @mock.patch("tubee.models.channel.Channel.subscribe")
    def test_channel_activate(self, mocked_subscribe):
        self.init_channel()
        mocked_subscribe.return_value = False
        with self.assertRaises(RuntimeError):
            self.test_channel.activate()
        self.assertFalse(self.test_channel.active)
        mocked_subscribe.return_value = True
        results = self.test_channel.activate()
        self.assertTrue(results)
        self.assertTrue(self.test_channel.active)
        self.assertAlmostEqual(
            self.test_channel.subscribe_timestamp.timestamp(),
            datetime.utcnow().timestamp(),
            places=1,
        )
        with self.assertRaises(AttributeError):
            results = self.test_channel.activate()

    @mock.patch("tubee.models.channel.subscribe")
    def test_channel_subscribe(self, mocked_subscribe):
        self.init_channel()
        mocked_subscribe.return_value.success = False
        self.assertFalse(self.test_channel.subscribe())
        mocked_subscribe.return_value.success = True
        self.assertTrue(self.test_channel.subscribe())
