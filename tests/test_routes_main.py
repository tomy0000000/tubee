"""Test Cases of Routes Response"""
import unittest
from flask_login import current_user
from unittest.mock import patch
from tubee import create_app, db
from tubee.models import User, Subscription

class MainRoutesTestCase(unittest.TestCase):
    """Test Cases of Routes Response"""
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        self.client_username = "test_user"
        self.client_user_password = "test_password"

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # def test_dashboard(self):
    #     with patch("flask_login.current_user.subscriptions") as check:
    #         check.return_value = [
    #             Subscription(subscriber_username=self.client_username, subscribing_channel_id="test_channel_id_1"),
    #             Subscription(subscriber_username=self.client_username, subscribing_channel_id="test_channel_id_2")
    #         ]
    #         response = self.client.get("/")
    #         check.assert_called_once()
    #         self.assertEqual(response.status_code, 200)

    def test_register_login_logout(self):
        """
        Test if Root Page works Properly
        Routes
            login
            |________root_login
            |________logout
            main
            |________dashboard
        Forms
            LoginForm
        """

        # Dashboard Attempt
        response = self.client.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Please log in to access this page.", response.get_data(as_text=True))
        # Register
        response = self.client.get("/user/register")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Password Confirm", response.get_data(as_text=True))
        response = self.client.post("/user/register", data={
            "username": self.client_username,
            "password": self.client_user_password,
            "password_confirm": self.client_user_password
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.client_username, response.get_data(as_text=True))
        # Logout
        response = self.client.get("/user/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("MESSAGE", response.get_data(as_text=True))
        self.assertIn("Logged Out", response.get_data(as_text=True))
        # Login and redirect to Dashboard
        response = self.client.post("/user/login", data={
            "username": self.client_username,
            "password": self.client_user_password
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.client_username, response.get_data(as_text=True))
        # Logout again
        response = self.client.get("/user/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("MESSAGE", response.get_data(as_text=True))
        self.assertIn("Logged Out", response.get_data(as_text=True))
