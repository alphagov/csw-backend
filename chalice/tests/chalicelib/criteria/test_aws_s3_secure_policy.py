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

#    def test_init_client(self):
#        self.assertIn('list_roles', dir(self.subclass.client))
#
#    def test_get_data(self):
#        for key in self.test_data:
#            with self.subTest(key=key):
#                self.subclass.client.list_roles = lambda session: self.test_data[key]
#                item = self.subclass.get_data(None)
#                self.assertIsInstance(item, list, msg="the method must return a list of dictionaries")
#                # TODO: find out if get_data returning an empty list is a test failure
#                # You can make this conditional on whether we're testing on a pass or fail - maybe a list size 0
#                # is ok for pass, but not for fail
#
#    def test_translate(self):
#        for role in self.test_data.values():
#            with self.subTest():
#                translation = self.subclass.translate(role[0])
#                self.assertIsInstance(translation, dict, msg="The output of the translate method is not a dict.")
#                self.assertIn("resource_id", translation, msg="The key 'resource_id' was not in "
#                                                              "the output of the translate method.")
#                self.assertIn("resource_name", translation, msg="The key 'resource_name' was not in "
#                                                                "the output of the translate method.")
#                self.assertEqual(
#                    translation['resource_id'],
#                    role[0]['Arn'],
#                    msg="The resource ID does not match the role ARN."
#                )
#                self.assertEqual(
#                    translation['resource_name'],
#                    role[0]['RoleName'],
#                    msg="The resource name does not match the role name."
#                )
#
#    def test_evaluate_pass_list_of_users(self):
#        event = {}
#        whitelist = []
#        for item in self.test_data['pass-list-of-users']:
#            # tests
#            output = self._evaluate_invariant_assertions(event, item, whitelist)
#            self._evaluate_passed_status_assertions(item, output)
#
#    def test_evaluate_pass_single_user(self):
#        event = {}
#        whitelist = []
#        for item in self.test_data['pass-single-user']:
#            # tests
#            output = self._evaluate_invariant_assertions(event, item, whitelist)
#            self._evaluate_passed_status_assertions(item, output)
#
#    def test_evaluate_fail_invalid_account(self):
#        event = {}
#        whitelist = []
#        for item in self.test_data['fail-invalid-account']:
#            # tests
#            output = self._evaluate_invariant_assertions(event, item, whitelist)
#            self._evaluate_failed_status_assertions(item, output)
#            self.assertIn("not recognised", self.subclass.annotation)
#
#    def test_evaluate_fail_only_roles(self):
#        event = {}
#        whitelist = []
#        for item in self.test_data['fail-only-roles']:
#            output = self._evaluate_invariant_assertions(event, item, whitelist)
#            self._evaluate_failed_status_assertions(item, output)
#            self.assertIn("No trusted users", self.subclass.annotation)
#
#    def test_evaluate_fail_mixed_users(self):
#        event = {}
#        whitelist = []
#        for item in self.test_data['fail-mixed-users']:
#            # tests
#            output = self._evaluate_invariant_assertions(event, item, whitelist)
#            self._evaluate_failed_status_assertions(item, output)
#
#    def test_evaluate_fail_principal_service(self):
#        event = {}
#        whitelist = []
#        for item in self.test_data['fail-principal-service']:
#            # tests
#            output = self._evaluate_invariant_assertions(event, item, whitelist)
#            self._evaluate_failed_status_assertions(item, output)
#            self.assertIn("Invalid service", self.subclass.annotation)
