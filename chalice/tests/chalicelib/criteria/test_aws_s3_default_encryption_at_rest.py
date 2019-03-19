from chalicelib.criteria.aws_s3_default_encryption_at_rest import AwsS3DefaultEncryptionAtRest
from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from tests.chalicelib.criteria.test_data import S3_BUCKET_ENCRYPTION


class TestAwsS3DefaultEncryptionAtRest(CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert):

    @classmethod
    def setUpClass(cls):
        super(TestAwsS3DefaultEncryptionAtRest, cls).setUpClass()
        cls.test_data = S3_BUCKET_ENCRYPTION

    def setUp(self):
        super(TestAwsS3DefaultEncryptionAtRest, self).setUp()
        self.subclass = AwsS3DefaultEncryptionAtRest(self.app)
