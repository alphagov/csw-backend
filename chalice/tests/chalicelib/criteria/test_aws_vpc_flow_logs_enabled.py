from chalicelib.criteria.aws_vpc_flow_logs_enabled import AwsVpcFlowLogsEnabled
from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin,
    TestCaseWithAttrAssert,
)
from tests.chalicelib.criteria.test_data import VPC_FLOW_LOGS_VPCS, VPC_FLOW_LOGS_DATA
import unittest


@unittest.skip("Broken test")
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
                self.subclass.client.describe_vpcs = lambda session, region_name: self.test_data[
                    key
                ]
                self.subclass.client.describe_flow_logs = lambda session, vpc, region_name: self.test_data_logs[
                    key
                ]
                item = self.subclass.get_data(None, region=None)
                message = "get_data should return a list of dicts"
                self.assertIsInstance(item, list, msg=message)
                self.assertIsInstance(item[0], dict, msg=message)
                self.assertIn(
                    "FlowLog", item[0], msg="'FlowLog' key not added to VPC dict"
                )

    def test_translate(self):
        for item in self.test_data.values():
            with self.subTest():
                for vpc in item:
                    translation = self.subclass.translate(vpc)
                    self.assertIsInstance(
                        translation,
                        dict,
                        msg="The output of the translate method should be a dict",
                    )
                    self.assertIn(
                        "resource_id",
                        translation,
                        msg="The key 'resource_id' was not in "
                        "the output of the translate method.",
                    )
                    self.assertIn(
                        "resource_name",
                        translation,
                        msg="The key 'resource_name' was not in "
                        "the output of the translate method.",
                    )
                    self.assertEqual(
                        translation["resource_id"],
                        vpc["VpcId"],
                        msg="resource_id does not match the VPC id",
                    )
                    if "Tags" in vpc:
                        self.assertEqual(
                            translation["resource_name"],
                            vpc["Tags"][0]["Value"],
                            msg="resource_name does not match the VPC name",
                        )
                    else:
                        self.assertEqual(
                            translation["resource_name"],
                            "",
                            msg="resource_name should be an empty string if the VPC has no Name tag",
                        )

    def test_evaluate_pass(self):
        event = {}
        whitelist = {}
        key = "pass"
        for item in self.test_data[key]:
            item["FlowLog"] = self.test_data_logs[key]
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_fail(self):
        event = {}
        whitelist = {}
        key = "fail"
        for item in self.test_data[key]:
            item["FlowLog"] = self.test_data_logs[key]
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)
