import unittest

from chalice import Chalice
from chalicelib.criteria.criteria_default import CriteriaDefault


class TestCriteriaDefault(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = Chalice('test_app')
        
    def setUp(self):
        self.criteria_default = CriteriaDefault(self.app)
        
    def test_init_success(self):
        self.assertIsInstance(self.criteria_default, CriteriaDefault)

    def test_init_failure(self):
        self.assertNotIsInstance(self.criteria_default, Chalice)


if __name__ == '__main__':
    unittest.main()
