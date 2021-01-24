"""Test Cases of User Routes"""
import unittest

from tubee import create_app, db, login_manager
from tubee.models import User


class ChannelRoutesTestCase(unittest.TestCase):
    """Test Cases of User Routes"""

    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        self.client_username = "test_user"
        self.client_password = "test_password"

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_register(self):
        # Test redirect non-logined user to Login
        response = self.client.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Login</title>", response.get_data(as_text=True))
        self.assertIn(login_manager.login_message, response.get_data(as_text=True))

        # Test HTML Page
        response = self.client.get("/user/register")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Register</title>", response.get_data(as_text=True))

        # Test DataRequired validator
        response = self.client.post(
            "/user/register",
            data={"username": "", "password": "", "password_confirm": ""},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_data(as_text=True).count("This field is required."), 3
        )

        # Test Length validator
        for length in [5, 31]:
            response = self.client.post(
                "/user/register",
                data={
                    "username": "*" * length,
                    "password": "*" * length,
                    "password_confirm": "*" * length,
                },
                follow_redirects=True,
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.get_data(as_text=True).count(
                    "Field must be between 6 and 30 characters long."
                ),
                3,
            )

        # Test EqualTo validator
        response = self.client.post(
            "/user/register",
            data={
                "username": self.client_username,
                "password": self.client_password,
                "password_confirm": "*" * 10,
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_data(as_text=True).count("Password Mismatched!"),
            2,
        )

        # Test Full Register Topology
        response = self.client.post(
            "/user/register",
            data={
                "username": self.client_username,
                "password": self.client_password,
                "password_confirm": self.client_password,
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Subscriptions</title>", response.get_data(as_text=True))
        self.assertIn(self.client_username, response.get_data(as_text=True))

        # Test redirect logined user to Dashboard
        response = self.client.get("/user/register", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Subscriptions</title>", response.get_data(as_text=True))
        self.assertIn("You&#39;ve already logined!", response.get_data(as_text=True))

        # Test Taken Username
        self.client.get("/user/logout")
        response = self.client.post(
            "/user/register",
            data={
                "username": self.client_username,
                "password": self.client_password,
                "password_confirm": self.client_password,
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("The Username is Taken", response.get_data(as_text=True))

    def test_user_login_logout(self):
        db.session.add(User(self.client_username, self.client_password))
        db.session.commit()

        # Test DataRequired validator
        response = self.client.post(
            "/user/login",
            data={"username": "", "password": ""},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_data(as_text=True).count("This field is required."), 2
        )

        # Test Bad Login
        response = self.client.post(
            "/user/login",
            data={"username": self.client_username, "password": "*"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Login</title>", response.get_data(as_text=True))
        self.assertIn("Invalid username or password.", response.get_data(as_text=True))

        # Test Full Login Topology and redirect to Dashboard
        response = self.client.post(
            "/user/login",
            data={"username": self.client_username, "password": self.client_password},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Subscriptions</title>", response.get_data(as_text=True))
        self.assertIn(self.client_username, response.get_data(as_text=True))

        # Test redirect logined user to Dashboard
        response = self.client.get("/user/login", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Subscriptions</title>", response.get_data(as_text=True))
        self.assertIn("You&#39;ve already logined!", response.get_data(as_text=True))

        # Logout and redirect to Login
        response = self.client.get("/user/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Login</title>", response.get_data(as_text=True))
        self.assertIn("You&#39;ve Logged Out", response.get_data(as_text=True))

        # Test Full Login Topology and redirect to pre-defined redirected URL
        response = self.client.get("/user/setting", follow_redirects=True)
        self.assertIn(login_manager.login_message, response.get_data(as_text=True))
        response = self.client.post(
            "/user/login?next=%2Fuser%2Fsetting",
            data={"username": self.client_username, "password": self.client_password},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Setting</title>", response.get_data(as_text=True))
        self.assertIn(self.client_username, response.get_data(as_text=True))
