"""Test Cases of User Model"""
import unittest
from unittest import mock

from tubee import create_app, db
from tubee.exceptions import InvalidAction, ServiceNotAuth
from tubee.models import User


class UserModelTestCase(unittest.TestCase):
    """Test Cases of User Model"""

    def setUp(self):
        self.app = create_app("testing")
        self.app.config["SERVER_NAME"] = "test_host"
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.test_username = "test_user"
        self.test_user_password = "test_password"
        self.test_pushover_key = "test_pushover"
        self.test_channel_id = "UCBR8-60-B28hp2BmDPdntcQ"

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_mixins(self):
        u = User(username=self.test_username, password=self.test_user_password)
        self.assertIs(u.is_authenticated, True)
        self.assertIs(u.is_active, True)
        self.assertIs(u.is_anonymous, False)
        self.assertEqual(u.get_id(), self.test_username)

    def test_password_getter(self):
        u = User(username=self.test_username, password=self.test_user_password)
        with self.assertRaises(AttributeError):
            u.password

    def test_password_setter(self):
        with self.assertRaises(ValueError):
            u = User(username=self.test_username, password="*" * 5)
        with self.assertRaises(ValueError):
            u = User(username=self.test_username, password="*" * 32)
        u = User(username=self.test_username, password=self.test_user_password)
        self.assertIsNotNone(u._password_hash)

    def test_check_password(self):
        u = User(username=self.test_username, password=self.test_user_password)
        self.assertTrue(u.check_password(self.test_user_password))
        self.assertFalse(u.check_password("*"))

    @mock.patch("tubee.models.user.PushoverAPI")
    def test_pushover_getter(self, mocked_PushoverAPI):
        u = User(username=self.test_username, password=self.test_user_password)
        with self.assertRaises(ServiceNotAuth):
            u.pushover
        mocked_PushoverAPI.return_value.validate.return_value = {"status": 1}
        u.pushover = self.test_pushover_key
        self.assertIsNotNone(u._pushover_key)
        self.assertEqual(u.pushover, self.test_pushover_key)
        self.assertEqual(u.pushover, u._pushover_key)

    @mock.patch("tubee.models.user.PushoverAPI")
    def test_pushover_setter(self, mocked_PushoverAPI):
        u = User(username=self.test_username, password=self.test_user_password)
        mocked_PushoverAPI.return_value.validate.return_value = {"status": -1}
        with self.assertRaises(InvalidAction):
            u.pushover = self.test_pushover_key
        self.assertIsNone(u._pushover_key)
        mocked_PushoverAPI.return_value.validate.return_value = {"status": 1}
        u.pushover = self.test_pushover_key
        self.assertIsNotNone(u._pushover_key)
        self.assertEqual(u.pushover, self.test_pushover_key)

    @mock.patch("tubee.models.user.PushoverAPI")
    def test_pushover_deleter(self, mocked_PushoverAPI):
        u = User(username=self.test_username, password=self.test_user_password)
        mocked_PushoverAPI.return_value.validate.return_value = {"status": 1}
        u.pushover = self.test_pushover_key
        self.assertIsNotNone(u._pushover_key)
        self.assertEqual(u.pushover, self.test_pushover_key)

    @mock.patch("tubee.models.Subscription")
    @mock.patch("tubee.models.user.User.is_subscribing")
    @mock.patch("tubee.models.Channel")
    def test_subscribe_to(
        self, mocked_channel, mocked_is_subscribing, mocked_subscription
    ):
        u = User(username=self.test_username, password=self.test_user_password)

        mocked_channel.query.get.return_value = mock.MagicMock(id=self.test_channel_id)
        mocked_is_subscribing.return_value = True
        with self.assertRaises(InvalidAction):
            u.subscribe_to(self.test_channel_id)

        mocked_channel.query.get.return_value = None
        mocked_is_subscribing.return_value = False
        u.subscribe_to(self.test_channel_id)
        mocked_channel.assert_called()

