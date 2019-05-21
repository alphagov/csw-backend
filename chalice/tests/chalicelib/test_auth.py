import os
import unittest
import datetime
import random
import string

# Declare the app so that the models file can import it
os.environ["CSW_ENV"] = "test"
os.environ["CSW_PREFIX"] = "csw-test"
import app

from chalice import Chalice
from chalicelib.auth import AuthHandler
import google_auth_oauthlib.flow

class TestAuthHandler(unittest.TestCase):
    """
    Unit tests for the AuthHandler class

    Currently this does not work because the _init_ method for AuthHandler
    retrieves the SSM parameters from AWS.

    This means the unit tests can't run without credentials.
    """

    def setUp(self):
        """
        """

        self.app = Chalice("test")
        self.auth = AuthHandler(self.app)
        self.setUpAuthParameters()

    def setUpAuthParameters(self):
        self.auth.client_config = {
            "web":{
                "client_id":"randomstring.apps.googleusercontent.com",
                "project_id":"cloud-security-watch",
                "auth_uri":"https://accounts.google.com/o/oauth2/auth",
                "token_uri":"https://www.googleapis.com/oauth2/v3/token",
                "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
                "client_secret":"randomstring",
                "redirect_uris":[
                    "https://example.com/app",
                    "https://example.com/app/"
                ],
                "javascript_origins":[
                    "https://example.com"
                ]
            }
        }
        # Generate a random string to emulate the SSM parameter
        self.auth.token_secret = ''.join(random.choices(
            string.ascii_uppercase + string.ascii_lowercase + string.digits, k=128)
        )

    def test_init_success(self):
        """
        test that initialization works
        """

        self.assertIsInstance(self.auth, AuthHandler)

        self.assertIsNone(self.auth.flow)

        self.assertIsInstance(self.auth.token_algorithm, str)

        self.assertIsInstance(self.auth.cookie_expiration, datetime.timedelta)

        self.assertIsInstance(self.auth.email_domain, str)

        self.assertEqual(len(self.auth.scopes), 2)

        self.assertIsNone(self.auth.cookie)

        self.assertFalse(self.auth.logged_in)

        self.assertDictEqual(self.auth.login_data, {"authenticated": False, "is_registered": False})

    def test_init_failure(self):
        """
        test that not passing Chalice app object raises a type error
        """
        self.assertRaises(TypeError, AuthHandler)

    # TODO figure out how to test get_params

    def test_get_auth_flow(self):
        """
        Test creating the OAuth flow object
        TODO resolve pip requirements to remove deprecation warnings - CT-341
        """
        flow = self.auth.get_auth_flow("https://example.com")
        self.assertIsInstance(flow, google_auth_oauthlib.flow.Flow)

    def test_get_base_url(self):
        """
        Test the url generated from the request matches
        """

        # Create an example object to mock the request object
        class TestRequest:
            headers = {}

        # Set request header values
        protocol = "https"

        # Create mock request instance
        domain = "localhost"
        test_request = TestRequest()
        test_request.headers = {
            "X-Forwarded-Proto": protocol,
            "Host": domain
        }

        # Call the method
        url = self.auth.get_base_url(test_request)
        # Check the method returns the manually created url.
        # Test that the protocol matches
        # Test that the domain matches the host header
        # Test that /app is not appended to the URL
        self.assertEqual(url, protocol + "://" + domain)

        domain = "example.com"
        test_request.headers["Host"] = domain

        # Call the method
        url = self.auth.get_base_url(test_request)
        # Check the method returns the manually created url.
        # Test that the protocol matches
        # Test that the domain matches the host header
        # Test that /app is appended to the URL
        self.assertEqual(url, protocol + "://" + domain + "/app")

        os.environ["CSW_CF_DOMAIN"] = "custom-domain.com"

        test_request.headers["User-Agent"] = "Amazon CloudFront"
        custom_domain = os.environ["CSW_CF_DOMAIN"]

        # Call the method
        url = self.auth.get_base_url(test_request)
        # Check the method returns the manually created url.
        # Test that the protocol matches
        # Test that the env var domain is used instead of the host header
        # and that the /app path is not appended to the URL
        self.assertEqual(url, protocol + "://" + custom_domain)

    def test_get_read_jwt(self):

        # Create a static user record dict
        user = {
            "email": "someone@somewhere.com",
            "name": "Someone Something"
        }

        # Encode it using get_jwt
        jwt = self.auth.get_jwt(user)

        # Decodee it using read_jwt
        decode = self.auth.read_jwt(jwt)

        # Check the original dict is returned successfully
        self.assertDictEqual(user, decode)


if __name__ == "__main__":
    unittest.main()
