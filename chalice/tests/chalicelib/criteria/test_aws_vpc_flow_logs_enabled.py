from chalicelib.criteria.aws_vpc_flow_logs_enabled import AwsVpcFlowLogsEnabled
from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from tests.chalicelib.criteria.test_data import VPC_FLOW_LOGS_DATA


class TestAwsVpcFlowLogsEnabled(CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert):
    @classmethod
    def setUpClass(cls):
        super(TestAwsVpcFlowLogsEnabled, cls).setUpClass()
        cls.test_data = VPC_FLOW_LOGS_DATA

    def setUp(self):
        super(TestAwsVpcFlowLogsEnabled, self).setUp()
        self.subclass = AwsVpcFlowLogsEnabled(self.app)

    def test_init_client(self):
        with self.subTest():
            self.assertIn("describe_regions", dir(self.subclass.client))
            self.assertIn("describe_vpcs", dir(self.subclass.client))
            self.assertIn("describe_flow_logs", dir(self.subclass.client))
