from chalicelib.criteria.aws_couldtrail_logging import (
    CouldtrailLogHasErrors,
    CouldtrailLogNotInRegion,
    CouldtrailLogTurnedOff,
    CouldtrailLogNotToCST,
)
from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from tests.chalicelib.criteria.test_data import CLOUDTRAIL_LOGGING


class TestCouldtrailLoggingMixin(CriteriaSubclassTestCaseMixin):
    """
    Mixin class for the two key test case classes below
    """

    @classmethod
    def setUpClass(cls):
        """
        """
        super(TestCouldtrailLoggingMixin, cls).setUpClass()
        cls.test_data = CLOUDTRAIL_LOGGING

    def test_init_client(self):
        """
        test that the client support the correct API method
        """
        # TODO: dynamically importing dependancies from the file tested
        self.assertIn('describe_trusted_advisor_check_result', dir(self.subclass.client))

    def test_get_data(self):
        """
        """
        for key in CLOUDTRAIL_LOGGING:
            with self.subTest(key=key):
                # overwrite the client.describe_trusted_advisor_check_result(...) to return a static response
                self.subclass.client.describe_trusted_advisor_check_result = \
                    lambda session, checkId, language: CLOUDTRAIL_LOGGING[key]
                # output value
                item = self.subclass.get_data(None, checkId=self.subclass.check_id, language=self.subclass.language)
                # must return a dictionary with the three necessary keys
                msg = "the method must return a list of dictionaries"
                self.assertIsInstance(item, list, msg=msg)
                self.assertGreater(len(item), 0, msg='data must be a list with at least one element')

    ###
    # Test all five outputs below for pass/inapplicability,
    # in each subclassed test case overwrite the one that is supposed to fail
    ###

    def test_evaluate_all_pass(self):
        """
        Compliant case
        """
        # input params
        event = {}
        whitelist = []
        for item in CLOUDTRAIL_LOGGING['all_pass']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_off_in_regions(self):
        """
        Compliant case
        """
        # input params
        event = {}
        whitelist = []
        for item in CLOUDTRAIL_LOGGING['off_in_regions']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_has_errors(self):
        """
        Compliant case
        """
        # input params
        event = {}
        whitelist = []
        for item in CLOUDTRAIL_LOGGING['has_errors']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_fail_all_except_has_errors(self):
        """
        Non-applicable case
        """
        # input params
        event = {}
        whitelist = []
        for item in CLOUDTRAIL_LOGGING['fail_all']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)


class TestCouldtrailLogHasErrors(TestCouldtrailLoggingMixin, TestCaseWithAttrAssert):

    def setUp(self):
        """
        """
        super(TestCouldtrailLogHasErrors, self).setUpClass()
        self.subclass = CouldtrailLogHasErrors(self.app)

    def test_evaluate_has_errors(self):
        """
        Compliant case
        """
        # input params
        event = {}
        whitelist = []
        for item in CLOUDTRAIL_LOGGING['has_errors']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)

    def test_evaluate_fail_all_except_has_errors(self):
        """
        Non-applicable case
        """
        # input params
        event = {}
        whitelist = []
        for item in CLOUDTRAIL_LOGGING['fail_all']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)


class TestCouldtrailLogNotInRegion(TestCouldtrailLoggingMixin, TestCaseWithAttrAssert):

    def setUp(self):
        """
        """
        super(TestCouldtrailLogNotInRegion, self).setUpClass()
        self.subclass = CouldtrailLogNotInRegion(self.app)

    def test_evaluate_off_in_regions(self):
        """
        Compliant case
        """
        # input params
        event = {}
        whitelist = []
        for item in CLOUDTRAIL_LOGGING['off_in_regions']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)


class TestCouldtrailLogTurnedOff(TestCouldtrailLoggingMixin, TestCaseWithAttrAssert):

    def setUp(self):
        """
        """
        super(TestCouldtrailLogTurnedOff, self).setUpClass()
        self.subclass = CouldtrailLogTurnedOff(self.app)


class TestCouldtrailLogNotToCST(TestCouldtrailLoggingMixin, TestCaseWithAttrAssert):

    def setUp(self):
        """
        """
        super(TestCouldtrailLogNotToCST, self).setUpClass()
        self.subclass = CouldtrailLogNotToCST(self.app)
