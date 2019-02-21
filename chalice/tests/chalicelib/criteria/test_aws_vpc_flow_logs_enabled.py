from chalicelib.criteria.aws_vpc_flow_logs_enabled import AwsVpcFlowLogsEnabled
from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from tests.chalicelib.criteria.test_data import VPC_FLOW_LOGS_VPCS, VPC_FLOW_LOGS_DATA


class TestAwsVpcFlowLogsEnabled(CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert):
    @classmethod
    def setUpClass(cls):
        super(TestAwsVpcFlowLogsEnabled, cls).setUpClass()
        cls.test_data = VPC_FLOW_LOGS_VPCS
        cls.test_data_logs = VPC_FLOW_LOGS_DATA

    def setUp(self):
        super(TestAwsVpcFlowLogsEnabled, self).setUp()
        self.subclass = AwsVpcFlowLogsEnabled(self.app)

    def test_init_client(self):
        with self.subTest():
            self.assertIn("describe_regions", dir(self.subclass.client))
            self.assertIn("describe_vpcs", dir(self.subclass.client))
            self.assertIn("describe_flow_logs", dir(self.subclass.client))

    def test_get_data(self):
        for key in self.test_data:
            with self.subTest(key=key):
                self.subclass.client.describe_vpcs = lambda session, region_name: self.test_data[key]
                self.subclass.client.describe_flow_logs = lambda session, vpc, region_name: self.test_data_logs[key]
                item = self.subclass.get_data(None, region=None)
                message = "get_data should return a list of dicts"
                self.assertIsInstance(item, list, msg=message)
                self.assertIsInstance(item[0], dict, msg=message)
                self.assertIn("FlowLog", item[0], msg="'FlowLog' key not added to VPC dict")
