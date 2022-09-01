"""Test Cases of App Basics"""
import unittest

from tubee import create_app, db
from tubee.exceptions import TubeeError

ERROR_MESSAGE = "error_message"


def err_view_func():
    raise TubeeError(ERROR_MESSAGE)


class BasicsTestCase(unittest.TestCase):
    """Test Cases of App Basics"""

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        self.error_message = ERROR_MESSAGE
        self.app.debug = False
        self.test_path = "/error_handler_testing"
        self.test_api_path = "/api/error_handler_testing"
        self.app.add_url_rule(self.test_path, self.test_path, err_view_func)
        self.app.add_url_rule(self.test_api_path, self.test_api_path, err_view_func)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_http_error_handler(self):
        response = self.client.get("/err" * 10)
        self.assertEqual(response.status_code, 404)

    def test_exception_handler(self):
        response = self.client.get(self.test_path)
        self.assertEqual(response.status_code, 400)
        self.assertIn("text/html", response.headers.get("content-type"))
        self.assertIn(self.error_message, response.get_data(as_text=True))

    def test_api_handler(self):
        response = self.client.get(self.test_api_path)
        self.assertEqual(response.status_code, 400)
        self.assertIn("application/json", response.headers.get("content-type"))
        self.assertIn(self.error_message, response.get_data(as_text=True))
