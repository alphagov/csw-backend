from chalicelib.criteria.aws_s3_versioning import AwsS3Versioning
from tests.chalicelib.criteria.test_criteria_default import (CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert)
from tests.chalicelib.criteria.test_data import S3_VERSIONING_DATA


class TestAwsS3Versioning(CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert):

    @classmethod
    def setUpClass(cls):
        super(TestAwsS3Versioning, cls).setUpClass()
        cls.test_data = S3_VERSIONING_DATA

    def setUp(self):
        super(TestAwsS3Versioning, self).setUp()
        self.subclass = AwsS3Versioning(self.app)

    def test_init_client(self):
        self.assertIn("get_bucket_versioning", dir(self.subclass.client))

    def test_get_data(self):
        for key in self.test_data:
            with self.subTest(key=key):
                self.subclass.client.get_bucket_list = lambda session: self.test_data[key]
                self.subclass.client.get_bucket_versioning = lambda session, bucket_name: None
                item = self.subclass.get_data(None)
                self.assertIsInstance(item, dict, msg="get_data does not return a dict")
