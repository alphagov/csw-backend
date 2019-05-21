import os
import unittest
import datetime
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

# Declare the app so that the models file can import it
os.environ["CSW_ENV"] = "test"
os.environ["CSW_PREFIX"] = "csw-test"
import app

from chalice import Chalice
from chalicelib.auth import AuthHandler
from chalicelib.template_handler import TemplateHandler

class TestTemplateHandler(unittest.TestCase):
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
        self.app.auth = AuthHandler(self.app)
        self.templates = TemplateHandler(self.app)

    def test_init_success(self):
        """
        test that initialization works
        """

        self.assertIsInstance(self.templates, TemplateHandler)

        self.assertIsInstance(self.templates.env, Environment)

        self.assertFalse(self.templates.logged_in)
        self.assertDictEqual(self.templates.login_data, {})

    def test_get_template(self):
        """
        Test that the get_template returns an instance of
        jinja2.Template for a valid template file or None
        """

        real_template = 'denied.html'
        fake_template = 'fake.html'

        template = self.templates.get_template(real_template)
        self.assertIsInstance(template, Template)

        template = self.templates.get_template(fake_template)
        self.assertIsNone(template)

    def test_get_auth_handler(self):
        """
        Test that get_auth_handler returns an instance of AuthHandler
        """
        auth = self.templates.get_auth_handler()
        self.assertIsInstance(auth, AuthHandler)


if __name__ == "__main__":
    unittest.main()