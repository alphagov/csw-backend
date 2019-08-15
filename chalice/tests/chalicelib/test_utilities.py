import unittest
import json
from chalicelib.utilities import Utilities


class TestUtilities_to_json(unittest.TestCase):
    """
    Unit tests for the `utilities.to_json` method
    """

    def setUp(self):
        self.u = Utilities()
        self.obj = {}
        self.json = self.u.to_json(self.obj)
        self.loaded_obj = json.loads(self.json)

    def test_to_json_returns_json(self):
        """ Test `to_json` converts an object to valid JSON.
        """
        self.assertEqual(self.obj, self.loaded_obj)


class TestUtilities_get_typed_exception(unittest.TestCase):
    """
    Unit tests for the `utilities.get_typed_exception` method
    """

    def setUp(self):
        self.u = Utilities()
        try:
            raise ValueError
        except ValueError:
            self.tb = self.u.get_typed_exception()
        self.fragments = [
            "/tests/chalicelib/test_utilities.py",
            "line",
            "setUp",
            "ValueError",
        ]

    def test_get_typed_exception_contains_an_exception(self):
        """ Check get_typed_exception returns a formated exception.

        The Exception looks like
        File "/home/user/csw-backend/chalice/tests/chalicelib/test_utilities.py", line 30, in setUp
           raise ValueError
        ValueError
        """
        for s in self.fragments:
            with self.subTest(s=s):
                self.assertIn(s, self.tb)


if __name__ == "__main__":
    unittest.main()
