from chalicelib.criteria.aws_iam_roles_with_trust_relationship import AwsIamRolesWithTrustRelationship

from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from tests.chalicelib.criteria.test_data import IAM_ROLES_WITH_TRUST_RELATIONSHIP

class TestAwsIamRolesWithTrustRelationsip(CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert):

    @classmethod
    def setUpClass(cls):
        super(TestAwsIamRolesWithTrustRelationsip, cls).setUpClass()
        cls.test_data = IAM_ROLES_WITH_TRUST_RELATIONSHIP

    def setUp(self):
        """
        """
        super(TestAwsIamRolesWithTrustRelationsip, self).setUp()
        self.subclass = AwsIamRolesWithTrustRelationship(self.app)

    def test_init_client(self):
        self.assertIn('list_roles', dir(self.subclass.client))

    def test_get_data(self):
        for key in self.test_data:
            with self.subTest(key=key):
                self.subclass.client.list_roles = lambda session: self.test_data[key]
                item = self.subclass.get_data(None)
                self.assertIsInstance(item, list, msg="the method must return a list of dictionaries")
                # TODO: find out if get_data returning an empty list is a test failure
                # You can make this conditional on whether we're testing on a pass or fail - maybe a list size 0
                # is ok for pass, but not for fail

    def test_translate(self):
        for role in self.test_data.values():
            with self.subTest():
                translation = self.subclass.translate(role[0])
                self.assertIsInstance(translation, dict, msg="The output of the translate method is not a dict.")
                self.assertIn("resource_id", translation, msg="The key 'resource_id' was not in "
                                                              "the output of the translate method.")
                self.assertIn("resource_name", translation, msg="The key 'resource_name' was not in "
                                                                "the output of the translate method.")
                self.assertEqual(
                    translation['resource_id'],
                    role[0]['Arn'],
                    msg="The resource ID does not match the role ARN."
                )
                self.assertEqual(
                    translation['resource_name'],
                    role[0]['RoleName'],
                    msg="The resource name does not match the role name."
                )

    def test_evaluate_pass(self):
        event = {}
        whitelist = []
        for item in self.test_data['pass']: # depends on get_data
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_fail_invalid_user(self):
        event = {}
        whitelist = []
        for item in self.test_data['fail-invalid-user']: # depends on get_data
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)

    def test_evaluate_fail_principal_service(self):
        event = {}
        whitelist = []
        for item in self.test_data['fail-principal-service']: # depends on get_data
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)
