from chalicelib.criteria.aws_rds_encryption import RdsEncryption

from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from tests.chalicelib.criteria.test_data import RDS_ENCRYPTION


class TestRdsEncryption(CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert):

    @classmethod
    def setUpClass(cls):
        super(TestRdsEncryption, cls).setUpClass()
        cls.test_data = RDS_ENCRYPTION

    def setUp(self):
        """
        """
        super(TestRdsEncryption, self).setUp()
        self.subclass = RdsEncryption(self.app)

    def test_init_client(self):
        self.assertIn('describe_db_instances', dir(self.subclass.client))

    def test_only_origin_region_for_get_data_success(self):
        # overwrite the client.describe_db_instances to return the appropriate test data
        self.subclass.client.describe_db_instances = lambda session: self.test_data['pass']
        # output value
        item = self.subclass.get_data(None, region='eu-west-1')
        # must return a dictionary with the three necessary keys
        self.assertEqual(
            len(item), 
            1, 
            msg='The len of the list must be the DB instances with the same AvailabilityZone as the region'
        )

    def test_only_origin_region_for_get_data_failure(self):
        # overwrite the client.describe_db_instances to return the appropriate test data
        self.subclass.client.describe_db_instances = lambda session: self.test_data['pass']
        # output value
        item = self.subclass.get_data(None, region='eu-west-2')
        # must return a dictionary with the three necessary keys
        self.assertEqual(
            len(item), 
            0, 
            msg='The len of the list must be the DB instances with the same AvailabilityZone as the region'
        )

    def test_translate(self):
        translation = self.subclass.translate(self.test_data['fail']['DBInstances'][0])
        with self.subTest():
            self.assertIsInstance(
                translation, dict, 
                msg="The output of the translate method should be a dict"
            )
        with self.subTest():
            self.assertIn(
                "region", translation, 
                msg="The key 'region' was not in the output of the translate method."
            )
            self.assertIsInstance(
                translation['region'], str,
                msg="The value of 'region' must be a non-empty string"
            )
            self.assertGreater(
                len(translation['region']), 0,
                msg="The value of 'region' must be a non-empty string"
            )
        with self.subTest():
            self.assertIn(
                "resource_id", translation, 
                msg="The key 'resource_id' was not in the output of the translate method."
            )
            self.assertIsInstance(
                translation['resource_id'], str,
                msg="The value of 'resource_id' must be a non-empty string"
            )
            self.assertGreater(
                len(translation['resource_id']), 0,
                msg="The value of 'resource_id' must be a non-empty string"
            )
        with self.subTest():
            self.assertIn(
                "resource_name", translation, 
                msg="The key 'resource_name' was not in the output of the translate method."
            )
            self.assertIsInstance(
                translation['resource_name'], str,
                msg="The value of 'resource_name' must be a non-empty string"
            )
            self.assertGreater(
                len(translation['resource_name']), 0,
                msg="The value of 'resource_name' must be a non-empty string"
            )

    def test_evaluate_fail(self):
        for d in self.test_data['fail']['DBInstances']:
            with self.subTest(key=d):
                output = self._evaluate_invariant_assertions({}, d, [])
                self._evaluate_failed_status_assertions(d, output)

    def test_evaluate_pass(self):
        for d in self.test_data['pass']['DBInstances']:
            with self.subTest(key=d):
                output = self._evaluate_invariant_assertions({}, d, [])
                self._evaluate_passed_status_assertions(d, output)
