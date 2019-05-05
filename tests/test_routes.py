"""Test Cases of Routes Response"""
import unittest
from app import create_app, db
from app.models import User

class RoutesTestCase(unittest.TestCase):
    """Test Cases of Routes Response"""
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_root_login(self):
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
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("You Must Login First!", response.get_data(as_text=True))
        # Build User
        test_user = User("test_user", "HelloTubee")
        db.session.add(test_user)
        # Login and redirect to Dashboard
        response = self.client.post("/login", data={
            "username": "test_user",
            "password": "HelloTubee"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("You Must Login First!", response.get_data(as_text=True))
        self.assertIn("Channel Name", response.get_data(as_text=True))
        # Logout and Back to Login
        response = self.client.get("/login/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Welcome!", response.get_data(as_text=True))

    def test_hub_callback(self):
        pass
