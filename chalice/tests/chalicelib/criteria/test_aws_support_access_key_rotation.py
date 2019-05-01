import unittest

from chalicelib.criteria.aws_support_access_key_rotation import (
    AwsIamAccessKeyRotationYellow,
    AwsIamAccessKeyRotationRed,
)
from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin,
    TestCaseWithAttrAssert,
)
from tests.chalicelib.criteria.test_data import IAM_KEY_ROTATION_ITEMS


class TestAwsIamAccessKeyRotationYellow(
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
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
        cls.test_data = IAM_KEY_ROTATION_ITEMS

    def setUp(self):
        """
        """
        self.subclass = AwsIamAccessKeyRotationYellow(self.app)

    def test_init_success(self):
        """
        test that initialization works
        """
        self.assertIsInstance(self.subclass, AwsIamAccessKeyRotationYellow)

    def test_init_failure(self):
        """
        test that not passing Chalice app object raises a type error
        """
        self.assertRaises(TypeError, AwsIamAccessKeyRotationYellow)

    def test_init_client(self):
        """
        test that the client support the correct API method
        """
        # TODO: dynamically importing dependancies from the file tested
        self.assertIn(
            "describe_trusted_advisor_check_result", dir(self.subclass.client)
        )

    def test_get_data(self):
        """
        """
        # overwrite the client.describe_trusted_advisor_check_result(...) to return a static response
        self.subclass.client.describe_trusted_advisor_check_result = lambda session, checkId, language: self.test_data[
            "green"
        ][
            "result"
        ]
        # output value
        item = self.subclass.get_data(
            None, checkId=self.subclass.check_id, language=self.subclass.language
        )
        # must return a dictionary with the three necessary keys
        msg = "the method must return a list of dictionaries"
        with self.subTest():
            self.assertIsInstance(item, list, msg=msg)

    def test_evaluate(self):
        """
        yellow (status: warning) test
        """
        # input params
        event = {}
        whitelist = []
        for suite in self.test_data:
            for item in self.test_data[suite]["result"]["flaggedResources"]:
                with self.subTest():
                    # tests
                    output = self._evaluate_invariant_assertions(event, item, whitelist)
                    if item["status"] in ["warning", "error"]:
                        self._evaluate_failed_status_assertions(item, output)
                    else:
                        self._evaluate_passed_status_assertions(item, output)


class TestAwsIamAccessKeyRotationRed(TestAwsIamAccessKeyRotationYellow):
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
        self.assertIsInstance(self.subclass, AwsIamAccessKeyRotationRed)

    def test_init_failure(self):
        """
        test that not passing Chalice app object raises a type error
        """
        self.assertRaises(TypeError, AwsIamAccessKeyRotationRed)

    def test_evaluate(self):
        """
        yellow (status: warning) test
        """
        # input params
        event = {}
        whitelist = []
        for suite in self.test_data:
            for item in self.test_data[suite]["result"]["flaggedResources"]:
                with self.subTest():
                    # tests
                    output = self._evaluate_invariant_assertions(event, item, whitelist)
                    if item["status"] == "error":
                        self._evaluate_failed_status_assertions(item, output)
                    else:
                        self._evaluate_passed_status_assertions(item, output)
