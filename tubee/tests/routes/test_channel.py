"""Test Cases of Channel Routes"""
import unittest
from unittest import mock

from tubee import create_app, db
from tubee.models import User


class ChannelRoutesTestCase(unittest.TestCase):
    """Test Cases of Channel Routes"""

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        self.client_username = "test_user"
        self.client_user_password = "test_password"
        self.test_channel_id = "UCBR8-60-B28hp2BmDPdntcQ"
        db.session.add(User(self.client_username, self.client_user_password))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # def test_channel_page(self):
    #     pass
    # channel_page_url = self.app
    # response = self.client.get(, follow_redirects=True)
    # self.assertEqual(response.status_code, 200)
    # self.assertIn("You Must Login First", response.get_data(as_text=True))

    @mock.patch("tubee.routes.channel.current_user")
    def test_channel_subscribe(self, mocked_current_user):
        response = self.client.post(
            "/user/login",
            data={
                "username": self.client_username,
                "password": self.client_user_password,
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        mocked_current_user.subscribe_to.return_value = True
        self.client.get("/channel/subscribe")
        response = self.client.post(
            "/channel/subscribe",
            data={"channel_id": self.test_channel_id},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Subscribe Success", response.get_data(as_text=True))
        mocked_current_user.subscribe_to.return_value = False
        response = self.client.post(
            "/channel/subscribe",
            data={"channel_id": self.test_channel_id},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Oops! Subscribe Failed for some reason", response.get_data(as_text=True)
        )

    # def test_channel_unsubscribe(self):
    #     pass

    # def test_channel_callback(self):
    # pass
    # self.client.post("/channel/{channel_id}/callback".format(self.test_channel_id))
