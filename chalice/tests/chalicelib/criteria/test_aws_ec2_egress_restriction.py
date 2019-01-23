from chalicelib.criteria.aws_ec2_egress_restriction import EgressRestrition
from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from tests.chalicelib.criteria.test_data import EGRESS_RESTRICTION


class TestEgressRestrition(CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert):
    """
    Mixin class for the two key test case classes below
    """

    @classmethod
    def setUpClass(cls):
        """
        """
        super(TestEgressRestrition, cls).setUpClass()
        cls.test_data = EGRESS_RESTRICTION

    def setUp(self):
        """
        """
        super(TestEgressRestrition, self).setUpClass()
        self.subclass = EgressRestrition(self.app)

    def test_init_client(self):
        """
        test that the client ec2 the correct API method
        """
        self.assertIn('describe_security_groups', dir(self.subclass.client))

    def test_get_data(self):
        """
        """
        # overwrite the client.describe_trusted_advisor_check_result(...) to return a static response
        self.subclass.client.describe_security_groups = \
            lambda session: EGRESS_RESTRICTION['pass']
        # output value
        item = self.subclass.get_data(None)
        # must return a dictionary with the three necessary keys
        msg = "the method must return a list of dictionaries"
        print(item)
        with self.subTest():
            self.assertIsInstance(item, dict, msg=msg)

    def test_evaluate_pass(self):
        """
        """
        # input params
        event = {}
        whitelist = []
        for item in EGRESS_RESTRICTION['pass']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_fail(self):
        """
        """
        # input params
        event = {}
        whitelist = []
        for item in EGRESS_RESTRICTION['fail']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)

