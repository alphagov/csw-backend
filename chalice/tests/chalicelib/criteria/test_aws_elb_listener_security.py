from chalicelib.criteria.aws_support_elb_listener_security import (
    ELBListenerSecurityNoListener,
    ELBListenerSecurityPredefinedOutdated,
    ELBListenerSecurityProtocolDiscouraged,
    ELBListenerSecurityInsecureProtocol,
)
from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from tests.chalicelib.criteria.test_data import ELB_LISTENER_SECURITY


class TestELBListenerSecurityMixin(CriteriaSubclassTestCaseMixin):
    """
    Mixin class for the two key test case classes below
    """

    @classmethod
    def setUpClass(cls):
        """
        """
        super(TestELBListenerSecurityMixin, cls).setUpClass()
        cls.test_data = ELB_LISTENER_SECURITY

    def test_init_client(self):
        """
        test that the client support the correct API method
        """
        # TODO: dynamically importing dependancies from the file tested
        self.assertIn('describe_trusted_advisor_check_result', dir(self.subclass.client))

    def test_get_data(self):
        """
        """
        for key in ELB_LISTENER_SECURITY:
            with self.subTest(key=key):
                # overwrite the client.describe_trusted_advisor_check_result(...) to return a static response
                self.subclass.client.describe_trusted_advisor_check_result = \
                    lambda session, checkId, language: ELB_LISTENER_SECURITY[key]
                # output value
                item = self.subclass.get_data(None, checkId=self.subclass.check_id, language=self.subclass.language)
                # must return a dictionary with the three necessary keys
                msg = "the method must return a list of dictionaries"
                self.assertIsInstance(item, list, msg=msg)
                if key == 'no_elb':
                    self.assertEqual(len(item), 0, msg='data must be a list with no elements')
                else:
                    self.assertGreater(len(item), 0, msg='data must be a list with at least one element')

    ###
    # Test all five outputs below for pass/inapplicability,
    # in each subclassed test case overwrite the one that is supposed to fail
    ###

    def test_evaluate_all_clear(self):
        """
        Green case
        """
        # input params
        event = {}
        whitelist = []
        for item in ELB_LISTENER_SECURITY['all_clear']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_no_listener(self):
        """
        yellow, because no listener case
        """
        # input params
        event = {}
        whitelist = []
        for item in ELB_LISTENER_SECURITY['no_listener']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_predifined_outdated(self):
        """
        yellow because predefined cypher/protocol is outadated
        """
        # input params
        event = {}
        whitelist = []
        for item in ELB_LISTENER_SECURITY['predifined_outdated']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_protocol_discouraged(self):
        """
        yellow because predefined cypher/protocol is not recommended
        """
        # input params
        event = {}
        whitelist = []
        for item in ELB_LISTENER_SECURITY['protocol_discouraged']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_insecure_protocol(self):
        """
        red because predefined cypher/protocol is insecure
        """
        # input params
        event = {}
        whitelist = []
        for item in ELB_LISTENER_SECURITY['insecure_protocol']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)


class TestELBListenerSecurityNoListener(TestELBListenerSecurityMixin, TestCaseWithAttrAssert):

    def setUp(self):
        """
        """
        super(TestELBListenerSecurityNoListener, self).setUpClass()
        self.subclass = ELBListenerSecurityNoListener(self.app)

    def test_evaluate_no_listener(self):
        """
        green (status: ok) test, even though the key is potentially leaked
        """
        # input params
        event = {}
        whitelist = []
        for item in ELB_LISTENER_SECURITY['no_listener']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)


class TestELBListenerSecurityPredefinedOutdated(TestELBListenerSecurityMixin, TestCaseWithAttrAssert):

    def setUp(self):
        """
        """
        super(TestELBListenerSecurityPredefinedOutdated, self).setUpClass()
        self.subclass = ELBListenerSecurityPredefinedOutdated(self.app)

    def test_evaluate_predifined_outdated(self):
        """
        yellow because predefined cypher/protocol is outadated
        """
        # input params
        event = {}
        whitelist = []
        for item in ELB_LISTENER_SECURITY['predifined_outdated']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)


class TestELBListenerSecurityProtocolDiscouraged(TestELBListenerSecurityMixin, TestCaseWithAttrAssert):

    def setUp(self):
        """
        """
        super(TestELBListenerSecurityProtocolDiscouraged, self).setUpClass()
        self.subclass = ELBListenerSecurityProtocolDiscouraged(self.app)

    def test_evaluate_protocol_discouraged(self):
        """
        yellow because predefined cypher/protocol is not recommended
        """
        # input params
        event = {}
        whitelist = []
        for item in ELB_LISTENER_SECURITY['protocol_discouraged']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)


class TestELBListenerSecurityInsecureProtocol(TestELBListenerSecurityMixin, TestCaseWithAttrAssert):

    def setUp(self):
        """
        """
        super(TestELBListenerSecurityInsecureProtocol, self).setUpClass()
        self.subclass = ELBListenerSecurityInsecureProtocol(self.app)

    def test_evaluate_insecure_protocol(self):
        """
        red because predefined cypher/protocol is insecure
        """
        # input params
        event = {}
        whitelist = []
        for item in ELB_LISTENER_SECURITY['insecure_protocol']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)
