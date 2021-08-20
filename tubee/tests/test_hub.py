"""Test Cases of utils.hub"""
import unittest
import uuid
from os.path import dirname, join
from unittest import mock
from urllib.parse import urljoin

from tubee.utils import hub

GOOGLE_HUB = "https://pubsubhubbub.appspot.com/"
TEST_CALLBACK_URL = "https://tubee.tubee/channel/UCBR8-60-B28hp2BmDPdntcQ/callback"
TEST_TOPIC = (
    "https://www.youtube.com/xml/feeds/videos.xml?channel_id=UCBR8-60-B28hp2BmDPdntcQ"
)


class MockResponse:
    def __init__(self, status_code, text, url=None):
        self.status_code = status_code
        self.text = text
        self.url = url


def mock_details_request(*args, **kwargs):
    with open(join(dirname(__file__), "data", "Pubsubhubbub Details.html")) as file:
        text = file.read()
    return MockResponse(200, text, urljoin(args[0], args[1]))


def mock_subscribe_request(*args, **kwargs):
    return MockResponse(202, None)


class HubPackageTestCase(unittest.TestCase):
    """Test Cases of App Basics"""

    def setUp(self):
        self.lease_seconds = 300
        self.secret = str(uuid.uuid4())

    def tearDown(self):
        pass

    @mock.patch(
        "tubee.utils.hub._formal_post_request", side_effect=mock_subscribe_request
    )
    def test_hub_subscribe(self, mocked_func):
        results = hub.subscribe(GOOGLE_HUB, TEST_CALLBACK_URL, TEST_TOPIC)
        self.assertTrue(results.success)

    @mock.patch(
        "tubee.utils.hub._formal_post_request", side_effect=mock_subscribe_request
    )
    def test_hub_unsubscribe(self, mocked_func):
        results = hub.unsubscribe(GOOGLE_HUB, TEST_CALLBACK_URL, TEST_TOPIC)
        self.assertTrue(results.success)

    @mock.patch("tubee.utils.hub._formal_get_request", side_effect=mock_details_request)
    def test_hub_details(self, mocked_func):
        results = hub.details(GOOGLE_HUB, TEST_CALLBACK_URL, TEST_TOPIC)
        DETAILS_FIELDS = [
            "requests_url",
            "response_object",
            "state",
            "stat",
            "last_challenge",
            "expiration",
            "last_subscribe",
            "last_unsubscribe",
            "last_challenge_error",
            "last_notification_error",
            "last_notification",
        ]
        for field in DETAILS_FIELDS:
            self.assertIn(field, results)
        self.assertEqual(
            results["requests_url"], urljoin(GOOGLE_HUB, "subscription-details")
        )
