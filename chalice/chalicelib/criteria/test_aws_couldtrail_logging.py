import unittest

from chalice import Chalice
from chalicelib.criteria.aws_couldtrail_logging import AwsCouldtrailLogging
from chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from chalicelib.criteria.test_data import CLOUDTRAIL_LOGGING_ITEMS


class TestAwsCouldtrailLogging(
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
):
    """
    Unit tests for the CriteriaDefault class
    """

    @classmethod
    def setUpClass(cls):
        """
        initialise the the Chalice app objects once to reuse it in every test.
        """
        super(TestAwsCouldtrailLogging, cls).setUpClass()
        cls.test_data = CLOUDTRAIL_LOGGING_ITEMS

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
        self.assertIn('get_trail_status', item, msg=msg)

    def _evaluate_failed_status_additional_assertions(self, item, output):
        """
        additional yellow/red tests
        """
        msg = '''
            evaluate must have an annotation key with value a string
            containing the home region and name of all failed trails
        '''
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
        item = self.test_data['yellow']
        whitelist = []
        # tests
        output = self._evaluate_invariant_assertions(event, item, whitelist)
        self._evaluate_failed_status_assertions(item, output)
        self._evaluate_failed_status_additional_assertions(item, output)
        with self.subTest():
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
        item = self.test_data['red']
        whitelist = []
        # first test the invariants and get the evaluate method's output
        output = self._evaluate_invariant_assertions(event, item, whitelist)
        self._evaluate_failed_status_assertions(item, output)
        self._evaluate_failed_status_additional_assertions(item, output)

    def test_evaluate_very_red(self):
        """
        red again test, but when no trails exist
        """
        # input params
        event = {}
        item = self.test_data['very_red']
        whitelist = []
        # first test the invariants and get the evaluate method's output
        output = self._evaluate_invariant_assertions(event, item, whitelist)
        self._evaluate_failed_status_assertions(item, output)
        self.assertGreater(
            len(self.subclass.annotation),
            0,
            msg='must indicate the absence of any trails'
        )


if __name__ == '__main__':
    unittest.main()
