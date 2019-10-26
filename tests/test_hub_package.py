"""Test Cases of helper.hub"""
import unittest
import uuid
from tubee.helper import hub

class HubPackageTestCase(unittest.TestCase):
    """Test Cases of App Basics"""
    def setUp(self):
        self.callback = "https://pubsubhubbub.appspot.com/"
        self.topic = "https://www.youtube.com/xml/feeds/videos.xml?channel_id=UCBR8-60-B28hp2BmDPdntcQ"
        self.lease_seconds = 300
        self.secret = str(uuid.uuid4())

    def tearDown(self):
        pass

    def test_subscribe_details_unsubscribe(self):
        # Subscribe
        results = hub.subscribe(self.callback, self.topic)
        self.assertEqual(results.status_code, 202)
        self.assertTrue(results.success)
        # Details
        # TODO: Expand Test of Details
        # GOOGLE HUB IS BACK, HORRAY
        results = hub.details(self.callback, self.topic)
        self.assertIn("requests_url", results)
        self.assertIn("response_object", results)
        self.assertIn("state", results)
        self.assertIn("stat", results)
        self.assertIn("last_challenge", results)
        self.assertIn("expiration", results)
        self.assertIn("last_subscribe", results)
        self.assertIn("last_unsubscribe", results)
        self.assertIn("last_challenge_error", results)
        self.assertIn("last_notification_error", results)
        self.assertIn("last_notification", results)
        # Unsubscribe
        results = hub.unsubscribe(self.callback, self.topic)
        self.assertEqual(results.status_code, 202)
        self.assertTrue(results.success)
