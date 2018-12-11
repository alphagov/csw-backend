from chalicelib.criteria.aws_exposed_key import AwsIamExposedAccessKey
from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from tests.chalicelib.criteria.test_data import IAM_KEY_EXPOSED_ITEMS


class TestAwsIamExposedAccessKey(CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert):
    """
    Unit tests for the CriteriaDefault class
    """

    @classmethod
    def setUpClass(cls):
        """
        """
        super(TestAwsIamExposedAccessKey, cls).setUpClass()
        cls.test_data = IAM_KEY_EXPOSED_ITEMS

    def setUp(self):
        """
        """
        super(TestAwsIamExposedAccessKey, self).setUpClass()
        self.subclass = AwsIamExposedAccessKey(self.app)

    def test_init_success(self):
        """
        test that initialization works
        """
        self.assertIsInstance(
            self.subclass, AwsIamExposedAccessKey
        )

    def test_init_failure(self):
        """
        test that not passing Chalice app object raises a type error
        """
        self.assertRaises(TypeError, AwsIamExposedAccessKey)

    def test_init_client(self):
        """
        test that the client support the correct API method
        """
        # TODO: dynamically importing dependancies from the file tested
        self.assertIn('describe_trusted_advisor_check_result', dir(self.subclass.client))

    def test_get_data(self):
        """
        """
        # overwrite the client.describe_trusted_advisor_check_result(...) to return a static response
        self.subclass.client.describe_trusted_advisor_check_result = \
            lambda session, checkId, language: IAM_KEY_EXPOSED_ITEMS['green']['result']
        # output value
        item = self.subclass.get_data(None, checkId=self.subclass.check_id, language=self.subclass.language)
        # must return a dictionary with the three necessary keys
        msg = "the method must return a list of dictionaries"
        with self.subTest():
            self.assertIsInstance(item, list, msg=msg)

    def test_evaluate_green(self):
        """
        green (status: ok) test
        """
        # input params
        event = {}
        whitelist = []
        for item in IAM_KEY_EXPOSED_ITEMS['green']['result']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_red(self):
        """
        red (status: error) test
        """
        # input params
        event = {}
        whitelist = []
        for item in IAM_KEY_EXPOSED_ITEMS['red']['result']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            if item['status'] == 'error':
                self._evaluate_failed_status_assertions(item, output)
            else:
                self._evaluate_passed_status_assertions(item, output)
