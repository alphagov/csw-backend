import unittest

from chalice import Chalice
from chalicelib.criteria.aws_couldtrail_logging import AwsCouldtrailLogging


class TestAwsCouldtrailLogging(unittest.TestCase):
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
        #TODO: test vars not from the base

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
        self.aws_couldtrail_logging.get_data(session, **kwargs)
        self.fail('Not implemented yet')
    
    def test_translate(self):
        """
        """
        # input params
        data = None
        # output value
        self.aws_couldtrail_logging.translate(data)
        self.fail('Not implemented yet')

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
        item = {'status': 'ok'}
        whitelist = []
        # first test the invariants and get the evaluate method's output
        output = self._evaluate_invariant_assertions(event, item, whitelist)
        # green tests
        self.assertNotIn('annotation', output)
        self.assertEqual(self.aws_couldtrail_logging.annotation, '')
        self.assertTrue(output['is_compliant'])
        self.assertTrue(output['is_applicable'])
        self.assertEqual(output['status_id'], 2)

    def _evaluate_failed_status_assertions(self, output):
        """
        yellow/red tests
        """
        self.assertIn('annotation', output)
        self.assertIsInstance(self.aws_couldtrail_logging.annotation, str)
        self.assertGreater(self.aws_couldtrail_logging.annotation, 0)
        self.assertFalse(output['is_compliant'])
        self.assertTrue(output['is_applicable'])
        self.assertEqual(output['status_id'], 3)

    def test_evaluate_yellow(self):
        """
        yellow (status: warning) test
        """
        # input params
        event = {}
        item = {'status': 'warning'}
        whitelist = []
        # tests
        output = self._evaluate_invariant_assertions(event, item, whitelist)
        self._evaluate_failed_status_assertions(output)

    def test_evaluate_red(self):
        """
        red (status: error) test
        """
        # input params
        event = {}
        item = {'status': 'error'}
        whitelist = []
        # first test the invariants and get the evaluate method's output
        output = self._evaluate_invariant_assertions(event, item, whitelist)
        self._evaluate_failed_status_assertions(output)


if __name__ == '__main__':
    unittest.main()