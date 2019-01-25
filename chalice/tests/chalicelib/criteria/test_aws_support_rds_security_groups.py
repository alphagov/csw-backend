from chalicelib.criteria.aws_support_rds_security_groups import (
    AwsSupportRDSSecurityGroupsYellow,
    AwsSupportRDSSecurityGroupsRed,
)
from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from tests.chalicelib.criteria.test_data import RDS_SECURITY_GROUPS


class TestAwsSupportRDSSecurityGroupsMixin(CriteriaSubclassTestCaseMixin):
    """
    Mixin class for the two key test case classes below
    """

    @classmethod
    def setUpClass(cls):
        """
        """
        super(TestAwsSupportRDSSecurityGroupsMixin, cls).setUpClass()
        cls.test_data = RDS_SECURITY_GROUPS

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
            lambda session, checkId, language: self.test_data
        # output value
        item = self.subclass.get_data(None, checkId=self.subclass.check_id, language=self.subclass.language)
        # must return a dictionary with the three necessary keys
        msg = "the method must return a list of dictionaries"
        self.assertIsInstance(item, list, msg=msg)

    def test_evaluate_pass(self):
        """
        Compliant case
        """
        # input params
        event = {}
        whitelist = []
        for item in self.test_data['result']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)


class TestAwsSupportRDSSecurityGroupsYellow(TestAwsSupportRDSSecurityGroupsMixin, TestCaseWithAttrAssert):

    def setUp(self):
        """
        """
        super(TestAwsSupportRDSSecurityGroupsYellow, self).setUpClass()
        self.subclass = AwsSupportRDSSecurityGroupsYellow(self.app)


class TestAwsSupportRDSSecurityGroupsRed(TestAwsSupportRDSSecurityGroupsMixin, TestCaseWithAttrAssert):

    def setUp(self):
        """
        """
        super(TestAwsSupportRDSSecurityGroupsRed, self).setUpClass()
        self.subclass = AwsSupportRDSSecurityGroupsRed(self.app)
