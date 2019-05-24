"""Test Cases of Routes of Channel"""
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
        self.client_username = "test_user"
        self.client_user_password = "test_password"
        self.test_channel_id = ""
        db.session.add(User(self.client_username, self.client_user_password))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_channel_page(self):
        pass
        # channel_page_url = self.app
        # response = self.client.get(, follow_redirects=True)
        # self.assertEqual(response.status_code, 200)
        # self.assertIn("You Must Login First", response.get_data(as_text=True))
    
    def test_subscribe(self):
        pass
        # response = self.client.get("/", follow_redirects=True)
        # self.assertEqual(response.status_code, 200)
        # self.assertIn("You Must Login First", response.get_data(as_text=True))

    def test_unsubscribe(self):
        pass

    def test_callback(self):
        pass
        # self.client.post("/channel/{channel_id}/callback".format(self.test_channel_id))
