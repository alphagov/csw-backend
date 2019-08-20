import unittest
#from chalice import Chalice
from app import CloudSecurityWatch


class TestClientDefault(unittest.TestCase):
    """
    Unit tests for the CriteriaDefault class
    """

    @classmethod
    def setUpClass(cls):
        """
        initialise the the Chalice app objects once to reuse it in every test
        """
        cls.app = CloudSecurityWatch("test_app")


if __name__ == "__main__":
    unittest.main()