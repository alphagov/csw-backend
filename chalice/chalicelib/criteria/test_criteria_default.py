"""
CriteriaDefault unit tests and Mixin for all its subclasses TestCases
"""

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
        cls.empty_summary = {
            'all': {
                'display_stat': 0,
                'category': 'all',
                'modifier_class': 'tested'
            },
            'applicable': {
                'display_stat': 0,
                'category': 'tested',
                'modifier_class': 'precheck'
            },
            'non_compliant': {
                'display_stat': 0,
                'category': 'failed',
                'modifier_class': 'failed'
            },
            'compliant': {
                'display_stat': 0,
                'category': 'passed',
                'modifier_class': 'passed'
            },
            'not_applicable': {
                'display_stat': 0,
                'category': 'ignored',
                'modifier_class': 'passed'
            },
            'regions': {
                'list': [],
                'count': 0
            }
        }
        
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
        
    def test_get_session(self):
        """
        test the get_session method for success and failure
        """
        self.assertFalse(self.criteria_default.get_session())
        #TODO: find acount/role params to test for success returning a string
        
    def test_describe(self):
        """
        test the describe method for success and failure
        """
        describe = self.criteria_default.describe()
        self.assertIsInstance(describe, dict)
        keys = [
            'title', 'description', 'why_is_it_important', 'how_do_i_fix_it',
        ]
        for key in describe:
            self.assertIn(key, keys)
        
    def test_get_data(self):
        """
        test the get_data method for output for any input
        """
        self.assertEqual(self.criteria_default.get_data('any_input'), [])
    
    #TODO: test_build_evaluation

    def test_get_status(self):
        """
        black box test for the get_status method
        """
        eval_dicts = [
            {'is_compliant': False, 'is_applicable': False, },
            {'is_compliant': False, 'is_applicable': True, },
            {'is_compliant': True, 'is_applicable': False, },
            {'is_compliant': True, 'is_applicable': True, },
        ]
        # test for return of 2 implying a
        self.assertEqual(
            self.criteria_default.get_status(eval_dicts[0]), 2
        )
        self.assertEqual(
            self.criteria_default.get_status(eval_dicts[2]), 2
        )
        self.assertEqual(
            self.criteria_default.get_status(eval_dicts[3]), 2
        )
        # test for fail which returns 3
        self.assertEqual(
            self.criteria_default.get_status(eval_dicts[1]), 3
        )
        
    def test_empty_summary(self):
        """
        test the empty_summary method
        """
        self.assertEqual(
            self.criteria_default.empty_summary(),
            self.empty_summary
        )
        
    #TODO: test_empty_summary


if __name__ == '__main__':
    unittest.main()
