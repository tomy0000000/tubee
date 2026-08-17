"""Test Cases of Main Routes"""

import unittest

from tubee import create_app, db
from tubee.models import User

# from unittest import mock


class MainRoutesTestCase(unittest.TestCase):
    """Test Cases of Main Routes"""

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        self.client_username = "test_user"
        self.client_user_password = "test_password"
        self.test_channel_ids = [f"test_channel_id_{i}" for i in range(10)]
        db.session.add(User(self.client_username, self.client_user_password))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_main_dashboard_non_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        response = self.client.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Please log in to access this page.", response.get_data(as_text=True)
        )

    def test_main_dashboard(self):
        # FIXME: werkzeug v2+ makes mocking current_user difficult, see #50
        # @mock.patch("tubee.routes.main.current_user")
        # def test_main_dashboard(self, mocked_current_user):
        # mocked_current_user.subscriptions.outerjoin().order_by().all.return_value = [
        #     mock.MagicMock(channel_id=channel_id)
        #     for channel_id in self.test_channel_ids
        # ]
        response = self.client.post(
            "/user/login",
            data={
                "username": self.client_username,
                "password": self.client_user_password,
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        # for channel_id in self.test_channel_ids:
        #     self.assertIn(channel_id, response.get_data(as_text=True))
