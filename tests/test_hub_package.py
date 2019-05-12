"""Test Cases of helper.hub"""
import unittest
import uuid
from app.helper import hub

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
        # GOOGLE HUB IS DOWN FOR UNKNOWN REASON, SUSPEND THIS TEST
        # results = hub.details(self.callback, self.topic)
        # self.assertEqual(results.status_code, 200)
        # Unsubscribe
        results = hub.unsubscribe(self.callback, self.topic)
        self.assertEqual(results.status_code, 202)
        self.assertTrue(results.success)
