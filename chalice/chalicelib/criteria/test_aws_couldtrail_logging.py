import unittest

from chalice import Chalice
from chalicelib.criteria.test_data import CLOUDTRAIL_LOGGING_ITEMS
from chalicelib.criteria.aws_couldtrail_logging import AwsCouldtrailLogging
from chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)


class TestAwsCouldtrailLogging(
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
):
    """
    Unit tests for the CriteriaDefault class
    """

    def setUp(self):
        """
        """
        self.subclass = AwsCouldtrailLogging(self.app)

    def test_init_success(self):
        """
        test that initialization works
        """
        self.assertIsInstance(
            self.subclass, AwsCouldtrailLogging
        )

    def test_init_failure(self):
        """
        test that not passing Chalice app object raises a type error
        """
        self.assertRaises(TypeError, AwsCouldtrailLogging)

    def test_init_client(self):
        """
        test that all instance variables have the expected initial values
        """
        # dynamically importing dependancies from the file tested
        # gds_aws_client_class = getattr(
        #     importlib.import_module('chalicelib.aws.gds_aws_client'),
        #     'GdsAwsClient'
        # )
        # vars initialized with constants on class definition
        # self.assertEqual(
        #     self.subclass.ClientClass, gds_aws_client_class
        # )
        self.fail('import or write the appropriate client')

    def test_get_data(self):
        """
        """
        # input params
        session = None
        kwargs = {}  # None
        # output value
        item = self.subclass.get_data(session, **kwargs)
        # must return a dictionary with the three necessary keys
        msg = '''
            the method must return a dictionary with three keys:
            describe_trusted_advisor_check_result,
            describe_trails,
            get_trail_status,
        '''
        self.assertIsInstance(item, dict, msg=msg)
        self.assertIsInstance(
            item['describe_trusted_advisor_check_result']['result']['status'],
            dict,
            msg=msg
        )
        self.assertIn('describe_trails', item, msg=msg)
        self.assertIn('get_trail_status', ite, msg=msgm)

    def test_evaluate_green(self):
        """
        green (status: ok) test
        """
        # input params
        event = {}
        item = CLOUDTRAIL_LOGGING_ITEMS['green']
        whitelist = []
        # first test the invariants and get the evaluate method's output
        output = self._evaluate_invariant_assertions(event, item, whitelist)
        # green tests
        with self.subTest():
            self.assertNotIn(
                'annotation',
                output,
                msg='evaluate must not return an annotation when successful'
            )
        with self.subTest():
            self.assertEqual(
                self.subclass.annotation,
                '',
                msg='the annotation must be an blank string'
            )
        with self.subTest():
            self.assertTrue(output['is_compliant'])
        with self.subTest():
            self.assertTrue(output['is_applicable'])
        with self.subTest():
            self.assertEqual(output['status_id'], 2)

    def _evaluate_failed_status_assertions(self, item, output):
        """
        yellow/red tests
        """
        # test the status variables
        with self.subTest():
            self.assertFalse(output['is_compliant'])
        with self.subTest():
            self.assertTrue(output['is_applicable'])
        with self.subTest():
            self.assertEqual(output['status_id'], 3)
        # test that the instances annotation contains all necessary info
        msg = '''
            evaluate must have an annotation key with value a string
            containing the home region and name of all failed trails
        '''
        with self.subTest():
            self.assertIn('annotation', output, msg=msg)
        with self.subTest():
            self.assertIsInstance(self.subclass.annotation, str, msg=msg)
        for trail in item['describe_trails']['trailList']:
            with self.subTest(trail=trail):
                self.assertIn(
                    trail['HomeRegion'],
                    self.subclass.annotation,
                    msg=msg
                )
            with self.subTest(trail=trail):
                self.assertIn(
                    trail['Name'],
                    self.subclass.annotation,
                    msg=msg
                )

    def test_evaluate_yellow(self):
        """
        yellow (status: warning) test
        """
        # input params
        event = {}
        item = CLOUDTRAIL_LOGGING_ITEMS['yellow']
        whitelist = []
        # tests
        output = self._evaluate_invariant_assertions(event, item, whitelist)
        self._evaluate_failed_status_assertions(item, output)
        self.assertIn(
            item['get_trail_status']['LatestDeliveryError'],
            self.subclass.annotation,
            msg='evaluate must also contain the last delivery error'
        )

    def test_evaluate_red(self):
        """
        red (status: error) test
        """
        # input params
        event = {}
        item = CLOUDTRAIL_LOGGING_ITEMS['red']
        whitelist = []
        # first test the invariants and get the evaluate method's output
        output = self._evaluate_invariant_assertions(event, item, whitelist)
        self._evaluate_failed_status_assertions(item, output)


if __name__ == '__main__':
    unittest.main()
