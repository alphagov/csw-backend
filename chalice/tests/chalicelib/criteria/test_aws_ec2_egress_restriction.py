from chalicelib.criteria.aws_ec2_egress_restriction import UnrestrictedEgressSecurityGroups
from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from tests.chalicelib.criteria.test_data import EGRESS_RESTRICTION


class TestUnrestrictedEgressSecurityGroups(CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert):
    """
    Mixin class for the two key test case classes below
    """

    @classmethod
    def setUpClass(cls):
        """
        """
        super(TestUnrestrictedEgressSecurityGroups, cls).setUpClass()
        cls.test_data = EGRESS_RESTRICTION

    def setUp(self):
        """
        """
        super(TestUnrestrictedEgressSecurityGroups, self).setUpClass()
        self.subclass = UnrestrictedEgressSecurityGroups(self.app)

    def test_init_client(self):
        """
        test that the client ec2 the correct API method
        """
        self.assertIn('describe_security_groups', dir(self.subclass.client))

    def test_get_data(self):
        """
        """
        # overwrite the client.describe_trusted_advisor_check_result(...) to return a static response
        self.subclass.client.describe_security_groups = \
            lambda session: EGRESS_RESTRICTION['fail']['SecurityGroups']
        # output value
        item = self.subclass.get_data(None)
        # must return a dictionary with the three necessary keys
        msg = "the method must return a list of dictionaries"
        with self.subTest():
            self.assertIsInstance(item, list, msg=msg)

    def test_translate(self):
        """
        """
        # output value
        for case in EGRESS_RESTRICTION:
            for group in EGRESS_RESTRICTION[case]['SecurityGroups']:
                with self.subTest():
                    translation = self.subclass.translate(group)
                    self.assertIsInstance(translation, dict, msg="The output of the translate method is not a dict.")
                    self.assertIn("resource_id", translation, msg="The key 'resource_id' was not in the output of the translate method.")
                    self.assertIn("resource_name", translation, msg="The key 'resource_name' was not in the output of the translate method.")
                    self.assertEqual(
                        translation['resource_id'],
                        group['GroupId'],
                        msg='The resource ID does not match the Security Group ID.'
                    )
                    self.assertEqual(
                        translation['resource_name'],
                        group['GroupName'],
                        msg='The resource name does not match the Security Group name.'
                    )

    def test_evaluate_pass(self):
        """
        """
        # input params
        event = {}
        whitelist = []
        for item in EGRESS_RESTRICTION['pass']['SecurityGroups']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_fail(self):
        """
        """
        # input params
        event = {}
        whitelist = []
        for item in EGRESS_RESTRICTION['fail']['SecurityGroups']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)
