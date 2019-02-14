from chalicelib.criteria.aws_s3_versioning import AwsS3Versioning
from tests.chalicelib.criteria.test_criteria_default import (CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert)
from tests.chalicelib.criteria.test_data import S3_VERSIONING_BUCKETS, S3_VERSIONING_STATUS


class TestAwsS3Versioning(CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert):

    @classmethod
    def setUpClass(cls):
        super(TestAwsS3Versioning, cls).setUpClass()
        cls.test_data = S3_VERSIONING_BUCKETS
        cls.test_data_status = S3_VERSIONING_STATUS

    def setUp(self):
        super(TestAwsS3Versioning, self).setUp()
        self.subclass = AwsS3Versioning(self.app)

    def test_init_client(self):
        self.assertIn("get_bucket_versioning", dir(self.subclass.client))

    def test_get_data(self):
        for key in self.test_data:
            with self.subTest(key=key):
                self.subclass.client.get_bucket_list = lambda session: self.test_data[key]
                self.subclass.client.get_bucket_versioning = lambda session, bucket_name: self.test_data_status[key]
                item = self.subclass.get_data(None)
                self.assertIsInstance(item, list, msg="The method must return a list of dictionaries")
                for bucket in item:
                    self.assertIn('Versioning', bucket, msg="The dicts within the list must have a 'Versioning' key")
                    self.assertIsInstance(bucket['Versioning'], dict, msg="Versioning must be a dict")

    def test_evaluate_pass(self):
        event = {}
        whitelist = {}
        for item in self.test_data['pass']:
            item["Versioning"] = self.test_data_status['pass']
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_fail(self):
        event = {}
        whitelist = {}
        for item in self.test_data['fail']:
            item["Versioning"] = self.test_data_status['fail']
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)

    def test_evaluate_fail_with_status(self):
        event = {}
        whitelist = {}
        for item in self.test_data['fail_with_status']:
            item["Versioning"] = self.test_data_status['fail_with_status']
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)
