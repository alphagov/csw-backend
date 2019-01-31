from chalicelib.criteria.aws_ebs_public_snapshots import EBSPublicSnapshot
from tests.chalicelib.criteria.test_criteria_default import CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
from tests.chalicelib.criteria.test_data import EBS_PUBLIC_SNAPSHOTS


class TestEBSPublicSnapshot(CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert):
    """
    Mixin class for the two key test case classes below
    """

    @classmethod
    def setUpClass(cls):
        """
        """
        super(TestEBSPublicSnapshot, cls).setUpClass()
        cls.test_data = EBS_PUBLIC_SNAPSHOTS

    def setUp(self):
        """
        """
        super(TestEBSPublicSnapshot, self).setUpClass()
        self.subclass = EBSPublicSnapshot(self.app)

    def test_init_client(self):
        """
        test that the client support the correct API method
        """
        # TODO: dynamically importing dependancies from the file tested
        self.assertIn('describe_trusted_advisor_check_result', dir(self.subclass.client))

    def test_get_data(self):
        """
        """
        for key in EBS_PUBLIC_SNAPSHOTS:
            with self.subTest(key=key):
                # overwrite the client.describe_trusted_advisor_check_result(...) to return a static response
                self.subclass.client.describe_trusted_advisor_check_result = \
                    lambda session, checkId, language: EBS_PUBLIC_SNAPSHOTS[key]
                # output value
                item = self.subclass.get_data(None, checkId=self.subclass.check_id, language=self.subclass.language)
                # must return a dictionary with the three necessary keys
                msg = "the method must return a list of dictionaries"
                self.assertIsInstance(item, list, msg=msg)
                if key == 'fail':
                    self.assertGreater(len(item), 0, msg='data must be a list with at least one element')

    # evaluate() will never be called with non-applicable and pass data,
    # because we declare the key flaggedResources and it is an empty list

    def test_evaluate_fail(self):
        """
        Non-compliant case
        """
        # input params
        event = {}
        whitelist = []
        for item in EBS_PUBLIC_SNAPSHOTS['fail']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)
