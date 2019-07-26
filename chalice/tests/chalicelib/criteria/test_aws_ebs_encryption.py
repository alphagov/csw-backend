from chalicelib.criteria.aws_ebs_encryption import EbsEncryption

from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin,
    TestCaseWithAttrAssert,
)
from tests.chalicelib.criteria.test_data import EBS_ENCRYPTION


class TestEbsEncryption(CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert):
    @classmethod
    def setUpClass(cls):
        super(TestEbsEncryption, cls).setUpClass()
        cls.test_data = EBS_ENCRYPTION

    def setUp(self):
        """
        """
        super(TestEbsEncryption, self).setUp()
        self.subclass = EbsEncryption(self.app)

    def test_init_client(self):
        self.assertIn("describe_volumes", dir(self.subclass.client))

    def test_only_origin_region_for_get_data_success(self):
        # overwrite the client.describe_db_instances to return the appropriate test data
        self.subclass.client.describe_volumes = lambda session: self.test_data
        # output value
        item = self.subclass.get_data(None, region="us-west-2")
        # must return a dictionary with the three necessary keys
        self.assertEqual(
            len(item),
            3,
            msg="The len of the list must be the volumes with the same AvailabilityZone as the region",
        )

    def test_only_origin_region_for_get_data_failure(self):
        # overwrite the client.describe_db_instances to return the appropriate test data
        self.subclass.client.describe_volumes = lambda session: self.test_data
        # output value
        item = self.subclass.get_data(None, region="eu-west-1")
        # must return a dictionary with the three necessary keys
        self.assertEqual(
            len(item),
            0,
            msg="The len of the list must be the volumes with the same AvailabilityZone as the region",
        )

    def test_translate(self):
        translation = self.subclass.translate(self.test_data[0])
        with self.subTest():
            self.assertIsInstance(
                translation,
                dict,
                msg="The output of the translate method should be a dict",
            )
        with self.subTest():
            self.assertIn(
                "region",
                translation,
                msg="The key 'region' was not in the output of the translate method.",
            )
            self.assertIsInstance(
                translation["region"],
                str,
                msg="The value of 'region' must be a non-empty string",
            )
            self.assertGreater(
                len(translation["region"]),
                0,
                msg="The value of 'region' must be a non-empty string",
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
        output = self._evaluate_invariant_assertions({}, self.test_data[1], [])
        self._evaluate_failed_status_assertions(self.test_data[1], output)

    def test_evaluate_pass(self):
        output = self._evaluate_invariant_assertions({}, self.test_data[0], [])
        self._evaluate_passed_status_assertions(self.test_data[0], output)

    def test_evaluate_pass_by_exception(self):
        output = self._evaluate_invariant_assertions({}, self.test_data[2], [])
        self._evaluate_passed_by_exception_status_assertions(self.test_data[2], output)
