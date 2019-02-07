from chalicelib.criteria.aws_support_elb_security_groups import (
    ELBSecurityGroupsYellow,
    ELBSecurityGroupsRed,
)
from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from tests.chalicelib.criteria.test_data import ELB_SECURITY_GROUPS


class TestELBSecurityGroupsMixin(CriteriaSubclassTestCaseMixin):
    """
    Mixin class for the two key test case classes below
    """

    @classmethod
    def setUpClass(cls):
        """
        """
        super(TestELBSecurityGroupsMixin, cls).setUpClass()
        cls.test_data = ELB_SECURITY_GROUPS

    def test_init_client(self):
        """
        test that the client support the correct API method
        """
        # TODO: dynamically importing dependancies from the file tested
        self.assertIn('describe_trusted_advisor_check_result', dir(self.subclass.client))

    def test_get_data(self):
        """
        """
        for key in ELB_SECURITY_GROUPS:
            with self.subTest(key=key):
                # overwrite the client.describe_trusted_advisor_check_result(...) to return a static response
                self.subclass.client.describe_trusted_advisor_check_result = \
                    lambda session, checkId, language: ELB_SECURITY_GROUPS[key]
                # output value
                item = self.subclass.get_data(None, checkId=self.subclass.check_id, language=self.subclass.language)
                # must return a dictionary with the three necessary keys
                msg = "the method must return a list of dictionaries"
                self.assertIsInstance(item, list, msg=msg)
                if key != 'no_elb':
                    self.assertGreater(len(item), 0, msg='data must be a list with at least one element')

    ###
    # Test the three outputs below for pass/inapplicability,
    # in each subclassed test case overwrite the one that is supposed to fail
    ###

    def test_evaluate_no_elb(self):
        """
        Compliant case
        """
        # input params
        event = {}
        whitelist = []
        for item in ELB_SECURITY_GROUPS['no_elb']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_green(self):
        """
        Compliant case
        """
        # input params
        event = {}
        whitelist = []
        for item in ELB_SECURITY_GROUPS['green']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_yellow(self):
        """
        Compliant case
        """
        # input params
        event = {}
        whitelist = []
        for item in ELB_SECURITY_GROUPS['yellow']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)


class TestELBSecurityGroupsYellow(TestELBSecurityGroupsMixin, TestCaseWithAttrAssert):

    def setUp(self):
        """
        """
        super(TestELBSecurityGroupsYellow, self).setUpClass()
        self.subclass = ELBSecurityGroupsYellow(self.app)

    def test_evaluate_yellow(self):
        """
        Overwrite the case that must fail the check
        """
        # input params
        event = {}
        whitelist = []
        for item in ELB_SECURITY_GROUPS['yellow']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)


class TestELBSecurityGroupsRed(TestELBSecurityGroupsMixin, TestCaseWithAttrAssert):

    def setUp(self):
        """
        No data to emulate the red check's failure
        """
        super(TestELBSecurityGroupsRed, self).setUpClass()
        self.subclass = ELBSecurityGroupsRed(self.app)
