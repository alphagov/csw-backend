from chalicelib.criteria.aws_s3_versioning import AwsS3Versioning
from tests.chalicelib.criteria.test_criteria_default import (CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert)
from tests.chalicelib.criteria.test_data import S3_VERSIONING_DATA


class TestAwsS3Versioning(CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert):
    @classmethod
    def setupClass(cls):
        super(TestAwsS3Versioning, cls).setUpClass()
        cls.test_data = S3_VERSIONING_DATA

    def setUp(self):
        super(TestAwsS3Versioning, self).setUp()
        self.subclass = AwsS3Versioning(self.app)
