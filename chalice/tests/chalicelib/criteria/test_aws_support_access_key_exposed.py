from chalicelib.criteria.aws_support_access_key_exposed import (
    AwsIamPotentiallyExposedAccessKey,
    AwsIamSuspectedExposedAccessKey,
)
from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin,
    TestCaseWithAttrAssert,
)
from tests.chalicelib.criteria.test_data import IAM_KEY_EXPOSED_ITEMS


class TestAwsIamExposedAccessKeyMixin(CriteriaSubclassTestCaseMixin):
    """
    Mixin class for the two key test case classes below
    """

    @classmethod
    def setUpClass(cls):
        """
        """
        super(TestAwsIamExposedAccessKeyMixin, cls).setUpClass()
        cls.test_data = IAM_KEY_EXPOSED_ITEMS

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
        self.subclass.client.describe_trusted_advisor_check_result = lambda session, checkId, language: IAM_KEY_EXPOSED_ITEMS[
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


class TestAwsIamSuspectedExposedAccessKey(
    TestAwsIamExposedAccessKeyMixin, TestCaseWithAttrAssert
):
    def setUp(self):
        """
        """
        super(TestAwsIamSuspectedExposedAccessKey, self).setUpClass()
        self.subclass = AwsIamSuspectedExposedAccessKey(self.app)

    def test_evaluate_green(self):
        """
        green (status: ok) test
        """
        # input params
        event = {}
        whitelist = []
        for item in IAM_KEY_EXPOSED_ITEMS["green"]["result"]["flaggedResources"]:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_yellow_to_green(self):
        """
        green (status: ok) test, even though the key is potentially leaked
        """
        # input params
        event = {}
        whitelist = []
        for item in IAM_KEY_EXPOSED_ITEMS["red"]["result"]["flaggedResources"]:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_red(self):
        """
        yellow (status: error) test
        """
        # input params
        event = {}
        whitelist = []
        for item in IAM_KEY_EXPOSED_ITEMS["yellow"]["result"]["flaggedResources"]:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            if item["status"] == "error":
                self._evaluate_failed_status_assertions(item, output)
            else:
                self._evaluate_passed_status_assertions(item, output)


class TestAwsIamPotentiallyExposedAccessKey(
    TestAwsIamExposedAccessKeyMixin, TestCaseWithAttrAssert
):
    def setUp(self):
        """
        """
        super(TestAwsIamPotentiallyExposedAccessKey, self).setUpClass()
        self.subclass = AwsIamPotentiallyExposedAccessKey(self.app)

    def test_evaluate_green(self):
        """
        green (status: ok) test
        """
        # input params
        event = {}
        whitelist = []
        for item in IAM_KEY_EXPOSED_ITEMS["green"]["result"]["flaggedResources"]:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_yellow_to_green(self):
        """
        green (status: ok) test, even though the key is suspected
        """
        # input params
        event = {}
        whitelist = []
        for item in IAM_KEY_EXPOSED_ITEMS["yellow"]["result"]["flaggedResources"]:
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
        for item in IAM_KEY_EXPOSED_ITEMS["red"]["result"]["flaggedResources"]:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            if item["status"] == "error":
                self._evaluate_failed_status_assertions(item, output)
            else:
                self._evaluate_passed_status_assertions(item, output)
