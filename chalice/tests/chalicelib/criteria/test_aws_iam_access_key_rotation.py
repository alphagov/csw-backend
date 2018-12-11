import unittest

from chalicelib.criteria.aws_iam_access_key_rotation import (
    AwsIamAccessKeyRotationYellow, AwsIamAccessKeyRotationRed
)
from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from tests.chalicelib.criteria.test_data import IAM_KEY_ROTATION_ITEMS


class TestAwsIamAccessKeyRotationMixin(CriteriaSubclassTestCaseMixin):
    """
    Unit tests for the CriteriaDefault class
    """

    @classmethod
    def setUpClass(cls):
        """
        initialise the the Chalice app objects once to reuse it in every test.
        """
        super(TestAwsIamAccessKeyRotationMixin, cls).setUpClass()
        cls.test_data = IAM_KEY_ROTATION_ITEMS

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
            lambda session, checkId, language: self.test_data['green']['result']
        # output value
        item = self.subclass.get_data(None, checkId=self.subclass.check_id, language=self.subclass.language)
        # must return a dictionary with the three necessary keys
        msg = "the method must return a list of dictionaries"
        with self.subTest():
            self.assertIsInstance(item, list, msg=msg)
        # with self.subTest():
        #     self.assertIsInstance(
        #         item['result']['status'],
        #         dict,
        #         msg=msg
        #     )


class TestAwsIamAccessKeyRotationYellow(
    TestAwsIamAccessKeyRotationMixin, TestCaseWithAttrAssert
):
    """
    Unit tests for the Yellow subclass
    """

    @classmethod
    def setUpClass(cls):
        """
        initialise the the Chalice app objects once to reuse it in every test.
        """
        super(TestAwsIamAccessKeyRotationYellow, cls).setUpClass()

    def setUp(self):
        """
        """
        self.subclass = AwsIamAccessKeyRotationYellow(self.app)

    def test_init_success(self):
        """
        test that initialization works
        """
        self.assertIsInstance(
            self.subclass, AwsIamAccessKeyRotationYellow
        )

    def test_init_failure(self):
        """
        test that not passing Chalice app object raises a type error
        """
        self.assertRaises(TypeError, AwsIamAccessKeyRotationYellow)

    def test_evaluate_green(self):
        """
        green (status: ok) test
        """
        # input params
        event = {}
        whitelist = []
        for item in self.test_data['green']['result']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_yellow(self):
        """
        yellow (status: warning) test
        """
        # input params
        event = {}
        whitelist = []
        for item in self.test_data['yellow']['result']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            if item['status'] == 'warning':
                self._evaluate_failed_status_assertions(item, output)
            else:
                self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_red(self):
        """
        red (status: error) test
        """
        # input params
        event = {}
        whitelist = []
        for item in self.test_data['red']['result']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            if item['status'] == 'error':
                self._evaluate_failed_status_assertions(item, output)
            else:
                self._evaluate_passed_status_assertions(item, output)


class TestAwsIamAccessKeyRotationRed(
    TestAwsIamAccessKeyRotationMixin, TestCaseWithAttrAssert
):
    """
    Unit tests for the Red subclass
    """

    @classmethod
    def setUpClass(cls):
        """
        initialise the the Chalice app objects once to reuse it in every test.
        """
        super(TestAwsIamAccessKeyRotationRed, cls).setUpClass()

    def setUp(self):
        """
        """
        self.subclass = AwsIamAccessKeyRotationRed(self.app)

    def test_init_success(self):
        """
        test that initialization works
        """
        self.assertIsInstance(
            self.subclass, AwsIamAccessKeyRotationRed
        )

    def test_init_failure(self):
        """
        test that not passing Chalice app object raises a type error
        """
        self.assertRaises(TypeError, AwsIamAccessKeyRotationRed)


if __name__ == '__main__':
    unittest.main()
