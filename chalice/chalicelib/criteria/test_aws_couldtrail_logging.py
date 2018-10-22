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
        #TODO: remove if annotation again an empty string
        # self.assertSequenceEqual(self.criteria_default.annotation, '')
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

    def test_evaluate(self):
        """
        """
        # input params
        event = None
        item = None
        whitelist = None
        # output value
        output = self.aws_couldtrail_logging.evaluate(event, item, whitelist)
        # tests
        eval_keys = ['resource_id', 'compliance_type', 'resource_type']
        for key in eval_keys:
            self.assertIn(key, output)
        self.fail('Not implemented yet')


if __name__ == '__main__':
    unittest.main()