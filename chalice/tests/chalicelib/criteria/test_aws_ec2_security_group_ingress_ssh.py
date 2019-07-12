from chalicelib.criteria.aws_ec2_security_group_ingress_ssh import AwsEc2SecurityGroupIngressSsh

from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin,
    TestCaseWithAttrAssert,
)
from tests.chalicelib.criteria.test_data import EC2_SECURITY_GROUPS_SSH_INGRESS


class TestAwsEc2SecurityGroupIngressSsh(CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert):
    @classmethod
    def setUpClass(cls):
        super(TestAwsEc2SecurityGroupIngressSsh, cls).setUpClass()
        cls.test_data = EC2_SECURITY_GROUPS_SSH_INGRESS

    def setUp(self):
        """
        """
        super(TestAwsEc2SecurityGroupIngressSsh, self).setUp()
        self.subclass = AwsEc2SecurityGroupIngressSsh(self.app)

    def test_init_client(self):
        self.assertIn("describe_security_groups", dir(self.subclass.client))

    def test_translate(self):
        translation = self.subclass.translate(self.test_data["fail"][0])
        with self.subTest():
            self.assertIsInstance(
                translation,
                dict,
                msg="The output of the translate method should be a dict",
            )
        with self.subTest():
            self.assertIn(
                "resource_id",
                translation,
                msg="The key 'resource_id' was not in the output of the translate method.",
            )
            self.assertIsInstance(
                translation["resource_id"],
                str,
                msg="The value of 'resource_id' must be a non-empty string",
            )
            self.assertGreater(
                len(translation["resource_id"]),
                0,
                msg="The value of 'resource_id' must be a non-empty string",
            )
        with self.subTest():
            self.assertIn(
                "resource_name",
                translation,
                msg="The key 'resource_name' was not in the output of the translate method.",
            )
            self.assertIsInstance(
                translation["resource_name"],
                str,
                msg="The value of 'resource_name' must be a non-empty string",
            )
            self.assertGreater(
                len(translation["resource_name"]),
                0,
                msg="The value of 'resource_name' must be a non-empty string",
            )

    def test_evaluate_fail(self):
        for d in self.test_data["fail"]:
            with self.subTest(key=d):
                output = self._evaluate_invariant_assertions({}, d, [])
                self._evaluate_failed_status_assertions(d, output)

    def test_evaluate_pass(self):
        for d in self.test_data["pass"]:
            with self.subTest(key=d):
                output = self._evaluate_invariant_assertions({}, d, [])
                self._evaluate_passed_status_assertions(d, output)

    def test_evaluate_na(self):
        for d in self.test_data["na"]:
            with self.subTest(key=d):
                output = self._evaluate_invariant_assertions({}, d, [])
                self._evaluate_inapplicable_status_assertions(d, output)