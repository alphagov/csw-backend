import unittest

from chalice import Chalice
from chalicelib.criteria.test_data import CLOUDTRAIL_LOGGING_ITEMS
from chalicelib.criteria.aws_couldtrail_logging import AwsCouldtrailLogging


class TestAwsCouldtrailLogging(unittest.TestCase):
    """
    Unit tests for the CriteriaDefault class
    """

    @classmethod
    def setUpClass(cls):
        """
        initialise the the Chalice app objects once to reuse it in every test.
        """
        cls.app = Chalice('test_app')

    def setUp(self):
        """
        """
        self.aws_couldtrail_logging = AwsCouldtrailLogging(self.app)

    def test_init_success(self):
        """
        test that initialization works
        """
        self.assertIsInstance(
            self.aws_couldtrail_logging, AwsCouldtrailLogging
        )

    def test_init_failure(self):
        """
        test that not passing Chalice app object raises a type error
        """
        self.assertRaises(TypeError, AwsCouldtrailLogging)

    def test_init_state(self):
        """
        test that all instance variables have the expected initial values
        """
        self.assertTrue(self.aws_couldtrail_logging.active)
        self.assertSequenceEqual(
            self.aws_couldtrail_logging.resource_type,
            'AWS::Cloudtrail::Logging'
        )
        self.assertSequenceEqual(self.aws_couldtrail_logging.annotation, '')
        self.assertIsInstance(self.aws_couldtrail_logging.title, str)
        self.assertIsInstance(self.aws_couldtrail_logging.description, str)
        self.assertIsInstance(
            self.aws_couldtrail_logging.why_is_it_important, str
        )
        self.assertIsInstance(
            self.aws_couldtrail_logging.how_do_i_fix_it, str
        )
        # subclass specific attributes
        self.assertIsInstance(self.aws_couldtrail_logging.check_id, str)
        self.assertGreater(self.aws_couldtrail_logging.check_id, 0)
        self.assertIsInstance(self.aws_couldtrail_logging.language, str)
        self.assertGreater(self.aws_couldtrail_logging.language, 0)
        self.assertIsInstance(self.aws_couldtrail_logging.region, str)
        self.assertGreater(self.aws_couldtrail_logging.region, 0)
        self.assertIsInstance(self.aws_couldtrail_logging.title, str)
        self.assertGreater(self.aws_couldtrail_logging.title, 0)
        self.assertIsInstance(self.aws_couldtrail_logging.description, str)
        self.assertGreater(self.aws_couldtrail_logging.description, 0)
        self.assertIsInstance(
            self.aws_couldtrail_logging.why_is_it_important, str
        )
        self.assertGreater(self.aws_couldtrail_logging.why_is_it_important, 0)
        self.assertIsInstance(self.aws_couldtrail_logging.how_do_i_fix_it, str)
        self.assertGreater(self.aws_couldtrail_logging.how_do_i_fix_it, 0)

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
        #     self.aws_couldtrail_logging.ClientClass, gds_aws_client_class
        # )
        self.fail('import or write the appropriate client')

    def test_get_data(self):
        """
        """
        # input params
        session = None
        kwargs = {}  # None
        # output value
        item = self.aws_couldtrail_logging.get_data(session, **kwargs)
        # must return a dictionary with the three necessary keys
        self.assertIsInstance(item, dict)
        self.assertIsInstance(
            item['describe_trusted_advisor_check_result']['result']['status'],
            dict
        )
        self.assertIn('describe_trails', item)
        self.assertIn('get_trail_status', item)

    def test_translate(self):
        """
        """
        # input params
        data = None
        # output value
        output = self.aws_couldtrail_logging.translate(data)
        self.assertIsInstance(output, dict)
        self.assertIn('resource_id', output)
        self.assertIsInstance(output['resource_id'], str)
        self.assertIn('resource_name', output)
        self.assertIsInstance(output['resource_name'], str)

    def _evaluate_invariant_assertions(self, event, item, whitelist):
        """
        tests for invariants of all input combos
        """
        init_resource_type = self.aws_couldtrail_logging.resource_type
        # output value
        output = self.aws_couldtrail_logging.evaluate(event, item, whitelist)
        # tests
        self.assertIsInstance(output, dict)
        eval_keys = [
            'resource_type', 'resource_id', 'compliance_type',
            'is_compliant', 'is_applicable', 'status_id',
        ]
        for key in eval_keys:
            self.assertIn(key, output)
        self.assertEqual(
            self.aws_couldtrail_logging.resource_type, init_resource_type
        )
        return output

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
        self.assertNotIn('annotation', output)
        self.assertEqual(self.aws_couldtrail_logging.annotation, '')
        self.assertTrue(output['is_compliant'])
        self.assertTrue(output['is_applicable'])
        self.assertEqual(output['status_id'], 2)

    def _evaluate_failed_status_assertions(self, item, output):
        """
        yellow/red tests
        """
        # test the status variables
        self.assertFalse(output['is_compliant'])
        self.assertTrue(output['is_applicable'])
        self.assertEqual(output['status_id'], 3)
        # test that the instances annotation contains all necessary info
        self.assertIn('annotation', output)
        self.assertIsInstance(self.aws_couldtrail_logging.annotation, str)
        self.assertIn(
            item['describe_trails']['trailList']['HomeRegion'],
            self.aws_couldtrail_logging.annotation
        )
        self.assertIn(
            item['describe_trails']['trailList']['Name'],
            self.aws_couldtrail_logging.annotation
        )
        self.assertIn(
            item['get_trail_status']['LatestDeliveryError'],
            self.aws_couldtrail_logging.annotation
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
