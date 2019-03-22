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

    def test_init_client(self):
        self.assertIn('get_bucket_list', dir(self.subclass.client))
        self.assertIn('get_bucket_encryption', dir(self.subclass.client))

    def test_get_data(self):
        for key in self.test_data:
            with self.subTest(key=key):
                self.subclass.client.get_bucket_list = lambda session: self.test_data[key]
                item = self.subclass.get_data(None)
                msg = 'get_data should return a list of dictionaries'
                self.assertIsInstance(item, list, msg=msg)
                self.assertIn('Encryption', item[0], msg='The dictionary must have an encryption key')

    def test_evaluate_pass(self):
        event = {}
        whitelist = []
        for item in self.test_data['pass']:
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_fail(self):
        event = {}
        whitelist = []
        for item in self.test_data['fail']:
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)
            self.assertIn('encrypted', self.subclass.annotation)
