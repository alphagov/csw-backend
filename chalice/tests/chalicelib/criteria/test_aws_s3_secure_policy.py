from chalicelib.criteria.aws_s3_secure_policy import AwsS3SecurePolicy

from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from tests.chalicelib.criteria.test_data import S3_BUCKET_POLICIES


class TestAwsS3SecurePolicy(CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert):

    @classmethod
    def setUpClass(cls):
        super(TestAwsS3SecurePolicy, cls).setUpClass()
        cls.test_data = S3_BUCKET_POLICIES

    def setUp(self):
        """
        """
        super(TestAwsS3SecurePolicy, self).setUp()
        self.subclass = AwsS3SecurePolicy(self.app)

    def test_init_client(self):
        self.assertIn('get_bucket_list', dir(self.subclass.client))
        self.assertIn('get_bucket_policy', dir(self.subclass.client))

    def test_get_data(self):
        for key in self.test_data:
            with self.subTest(key=key):
                self.subclass.client.get_bucket_list = lambda session: self.test_data[key]
                self.subclass.client.get_bucket_policy = lambda session, bucket_name: None
                item = self.subclass.get_data(None)
                self.assertIsInstance(item, list, msg="The method must return a list of dictionaries")
                self.assertIn('Policy', item[0], msg="The dictionary must have a Policy key")

    def test_translate(self):
        for bucket in self.test_data.values():
            with self.subTest():
                translation = self.subclass.translate(bucket[0])
                self.assertIsInstance(translation, dict, msg="The output of the tranlsate method should be a dict")
                self.assertIn("resource_id", translation, msg="The key 'resource_id' was not in "
                                                              "the output of the translate method.")
                self.assertIn("resource_name", translation, msg="The key 'resource_name' was not in "
                                                                "the output of the translate method.")
                self.assertEqual(
                    translation['resource_id'],
                    "arn:aws:s3:::" + bucket[0]['Name'],
                    msg="resource_id does not match the bucket ARN"
                )
                self.assertEqual(
                    translation['resource_name'],
                    bucket[0]['Name'],
                    msg="resource_name does not match the bucket name"
                )

    def test_evaluate_pass(self):
        event = {}
        whitelist = []
        for item in self.test_data['pass']:
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_fail_no_policy(self):
        event = {}
        whitelist = []
        for item in self.test_data['fail_no_policy']:
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)
            self.assertIn("has no policy", self.subclass.annotation)

    def test_evaluate_fail_no_condition(self):
        event = {}
        whitelist = []
        for item in self.test_data['fail_no_condition']:
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)
            self.assertIn("policy does not have a condition", self.subclass.annotation)

    def test_evaluate_fail_no_secure_condition(self):
        event = {}
        whitelist = []
        for item in self.test_data['fail_no_secure_condition']:
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)
            self.assertIn("no SecureTransport", self.subclass.annotation)

    def test_evaluate_fail_only_insecure(self):
        event = {}
        whitelist = []
        for item in self.test_data['fail_only_insecure']:
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)
            self.assertIn("explicitly disallows HTTPS", self.subclass.annotation)