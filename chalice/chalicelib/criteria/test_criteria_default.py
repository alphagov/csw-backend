import importlib
import unittest

from chalice import Chalice
from chalicelib.criteria.criteria_default import CriteriaDefault


class TestCriteriaDefault(unittest.TestCase):
    """
    Unit tests for the CriteriaDefault class
    """

    @classmethod
    def setUpClass(cls):
        """
        initialise the the Chalice app objects once to reuse it in every test
        """
        cls.app = Chalice('test_app')
        
    def setUp(self):
        """
        initialise the class before every test
        """
        self.criteria_default = CriteriaDefault(self.app)
        
    def test_init_success(self):
        """
        test that initialization works
        """
        self.assertIsInstance(self.criteria_default, CriteriaDefault)

    def test_init_failure(self):
        """
        test that not passing Chalice app object raises a type error
        """
        self.assertRaises(TypeError, CriteriaDefault)

    def test_init_state(self):
        """
        test that all instance variables have the expected initial values
        """
        # dynamically importing dependancies from the file tested
        gds_aws_client_class = getattr(
            importlib.import_module('chalicelib.aws.gds_aws_client'),
            'GdsAwsClient'
        )
        # vars initialized with constants on class definition
        self.assertFalse(self.criteria_default.active)
        self.assertDictEqual(self.criteria_default.resources, {})
        self.assertSequenceEqual(
            self.criteria_default.resource_type, 'AWS::*::*'
        )
        self.assertSequenceEqual(self.criteria_default.annotation, '')
        self.assertEqual(
            self.criteria_default.ClientClass, gds_aws_client_class
        )
        self.assertIsNone(self.criteria_default.title)
        self.assertIsNone(self.criteria_default.description)
        self.assertIsNone(self.criteria_default.why_is_it_important)
        self.assertIsNone(self.criteria_default.how_do_i_fix_it)
        # vars initialized algorithmically at object instantiation
        self.assertIsInstance(
            self.criteria_default.app, Chalice
        )
        self.assertIsInstance(
            self.criteria_default.client, gds_aws_client_class
        )


if __name__ == '__main__':
    unittest.main()
