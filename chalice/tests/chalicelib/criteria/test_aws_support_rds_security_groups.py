from chalicelib.criteria.aws_support_rds_security_groups import (
    AwsSupportRDSSecurityGroupsYellow,
    AwsSupportRDSSecurityGroupsRed,
)
from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin,
    TestCaseWithAttrAssert,
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
        self.assertIn(
            "describe_trusted_advisor_check_result", dir(self.subclass.client)
        )

    def test_get_data(self):
        """
        """
        # overwrite the client.describe_trusted_advisor_check_result(...) to return a static response
        self.subclass.client.describe_trusted_advisor_check_result = (
            lambda session, checkId, language: self.test_data
        )
        self.subclass.get_resource_data = lambda session, region, flagged_resource: {
            "Description": "default VPC security group",
            "GroupName": "default",
            "IpPermissions": [
                {
                    "FromPort": 5432,
                    "IpProtocol": "tcp",
                    "IpRanges": [
                        {
                            "CidrIp": "0.0.0.0/0"
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": [],
                    "ToPort": 5432,
                    "UserIdGroupPairs": [
                        {
                            "GroupId": "sg-123234",
                            "UserId": "123234"
                        }
                    ]
                }
            ],
            "OwnerId": "123234",
            "GroupId": "sg-123345",
            "VpcId": "vpc-123234"
        }
        # output value
        item = self.subclass.get_data(
            None, checkId=self.subclass.check_id, language=self.subclass.language
        )
        # must return a dictionary with the three necessary keys
        msg = "the method must return a list of dictionaries"
        self.assertIsInstance(item, list, msg=msg)


class TestAwsSupportRDSSecurityGroupsYellow(
    TestAwsSupportRDSSecurityGroupsMixin, TestCaseWithAttrAssert
):
    def setUp(self):
        """
        """
        super(TestAwsSupportRDSSecurityGroupsYellow, self).setUpClass()
        self.subclass = AwsSupportRDSSecurityGroupsYellow(self.app)

    def test_evaluate_pass(self):
        """
        Compliant case
        """
        # input params
        event = {}
        whitelist = []
        for item in self.test_data["pass"]["result"]["flaggedResources"]:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_warn(self):
        """
        Compliant case
        """
        # input params
        event = {}
        whitelist = []
        for item in self.test_data["warn"]["result"]["flaggedResources"]:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)


class TestAwsSupportRDSSecurityGroupsRed(
    TestAwsSupportRDSSecurityGroupsMixin, TestCaseWithAttrAssert
):
    def setUp(self):
        """
        """
        super(TestAwsSupportRDSSecurityGroupsRed, self).setUpClass()
        self.subclass = AwsSupportRDSSecurityGroupsRed(self.app)

    def test_evaluate_pass(self):
        """
        Compliant case
        """
        # input params
        event = {}
        whitelist = []
        for item in self.test_data["pass"]["result"]["flaggedResources"]:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_fail(self):
        """
        Compliant case
        """
        # input params
        event = {}
        whitelist = []
        for item in self.test_data["fail"]["result"]["flaggedResources"]:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)
