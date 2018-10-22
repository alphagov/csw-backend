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
    
    def test_build_evaluation(self):
        """
        black box test of the build_evaluation method
        """
        # mock input params
        resource_id = 'any_string'
        compliance_type = 'COMPLIANT'
        event = {}
        resource_type = self.criteria_default.resource_type
        built_evaluation = self.criteria_default.build_evaluation(
            resource_id, compliance_type, event, resource_type
        )
        self.assertIsInstance(built_evaluation, dict)
        keys = [
            'resource_type', 'resource_id', 'compliance_type',
            'is_compliant', 'is_applicable', 'status_id',
        ]
        for key in built_evaluation.keys():
            self.assertIn(key, keys)
        # recall the method with the annotation optional param
        annotation = 'optional_string'
        built_evaluation = self.criteria_default.build_evaluation(
            resource_id, compliance_type, event, resource_type, annotation
        )
        self.assertIsInstance(built_evaluation, dict)
        self.assertIn('annotation', built_evaluation.keys())
        # return values tests for type correctness and values when possible
        self.assertEqual(built_evaluation['annotation'], annotation)
        self.assertEqual(built_evaluation['resource_type'], resource_type)
        self.assertEqual(built_evaluation['resource_id'], resource_id)
        self.assertEqual(built_evaluation['compliance_type'], compliance_type)
        self.assertTrue(built_evaluation['is_compliant'])
        self.assertTrue(built_evaluation['is_applicable'])
        self.assertEqual(
            built_evaluation['status_id'],
            self.criteria_default.get_status(built_evaluation)
        )
        # finally the remaining cases of compliance_type
        compliance_type = 'NON_COMPLIANT'
        built_evaluation = self.criteria_default.build_evaluation(
            resource_id, compliance_type, event, resource_type, annotation
        )
        self.assertFalse(built_evaluation['is_compliant'])
        self.assertTrue(built_evaluation['is_applicable'])
        self.assertEqual(
            built_evaluation['status_id'],
            self.criteria_default.get_status(built_evaluation)
        )
        compliance_type = 'NOT_APPLICABLE'
        built_evaluation = self.criteria_default.build_evaluation(
            resource_id, compliance_type, event, resource_type, annotation
        )
        self.assertFalse(built_evaluation['is_compliant'])
        self.assertFalse(built_evaluation['is_applicable'])
        self.assertEqual(
            built_evaluation['status_id'],
            self.criteria_default.get_status(built_evaluation)
        )
    
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
