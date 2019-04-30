import unittest
import datetime
import os
from chalice import Chalice
# This import is broken.
# from chalicelib.auth import AuthHandler
import google_auth_oauthlib.flow


@unittest.skip("Broken test")
class TestAuthHandler(unittest.TestCase):
    """
    Unit tests for the AuthHandler class
    """

    def setUp(self):
        """
        """
        os.environ['CSW_ENV'] = 'test'
        self.app = Chalice("test")
        self.auth = AuthHandler(self.app)

    def test_init_success(self):
        """
        test that initialization works
        """

        self.assertIsInstance(
            self.auth, AuthHandler
        )

        self.assertIsNone(
            self.auth.flow
        )

        self.assertIsInstance(
            self.auth.token_algorithm,
            str
        )

        self.assertIsInstance(
            self.auth.cookie_expiration,
            datetime.timedelta
        )

        self.assertIsInstance(
            self.auth.email_domain,
            str
        )

        self.assertEqual(
            len(self.auth.scopes),
            3
        )

        self.assertIsNone(
            self.auth.cookie
        )

        self.assertFalse(
            self.auth.logged_in
        )

        self.assertDictEqual(
            self.auth.login_data,
            {}
        )

    def test_init_failure(self):
        """
        test that not passing Chalice app object raises a type error
        """
        self.assertRaises(TypeError, AuthHandler)

    # TODO figure out how to test get_params

    def test_get_auth_flow(self):
        """
        test creating the OAuth flow object
        TODO resolve pip requirements to remove deprecation warnings - CT-341
        """
        flow = self.auth.get_auth_flow("https://example.com")
        self.assertIsInstance(
            flow,
            google_auth_oauthlib.flow.Flow
        )

    def test_get_request_url(self):
        """
        Test the url generated from the request matches
        """

        # Create an example object to mock the request object
        class TestRequest:
            headers = {}

        # Set request header values
        protocol = "https"
        domain = "example.com"

        # Create mock request instance
        test_request = TestRequest()
        test_request.headers = {
            "X-Forwarded-Proto": protocol,
            "Host": domain
        }

        # Call the method
        url = self.auth.get_request_url(test_request)

        # Check the method returns the manually created url.
        self.assertEqual(
            url,
            protocol+"://"+domain+"/app"
        )


if __name__ == '__main__':
    unittest.main()
