from chalicelib.criteria.aws_s3_bucket_permissions import (
    S3BucketReadAll,
    S3BucketOpenAccess,
    S3BucketWriteAll,
)
from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from tests.chalicelib.criteria.test_data import S3_BUCKET_PERMISSIONS


class TestS3BucketPermissionsMixin(CriteriaSubclassTestCaseMixin):
    """
    Mixin class for the two key test case classes below
    """

    @classmethod
    def setUpClass(cls):
        """
        """
        super(TestS3BucketPermissionsMixin, cls).setUpClass()
        cls.test_data = S3_BUCKET_PERMISSIONS

    def test_init_client(self):
        """
        test that the client support the correct API method
        """
        # TODO: dynamically importing dependancies from the file tested
        self.assertIn('describe_trusted_advisor_check_result', dir(self.subclass.client))

    def test_get_data(self):
        """
        """
        for key in S3_BUCKET_PERMISSIONS:
            with self.subTest(key=key):
                # overwrite the client.describe_trusted_advisor_check_result(...) to return a static response
                self.subclass.client.describe_trusted_advisor_check_result = \
                    lambda session, checkId, language: S3_BUCKET_PERMISSIONS[key]
                # output value
                item = self.subclass.get_data(None, checkId=self.subclass.check_id, language=self.subclass.language)
                # must return a dictionary with the three necessary keys
                msg = "the method must return a list of dictionaries"
                self.assertIsInstance(item, list, msg=msg)
                if key == 'non_applicable':
                    self.assertEqual(len(item), 0, msg='data must be a list with no elements')
                else:
                    self.assertGreater(len(item), 0, msg='data must be a list with at least one element')

    ###
    # Test all five outputs below for pass/inapplicability,
    # in each subclassed test case overwrite the one that is supposed to fail
    ###

    def test_evaluate_all_clear(self):
        """
        Compliant case
        """
        # input params
        event = {}
        whitelist = []
        for item in S3_BUCKET_PERMISSIONS['compliant']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_no_bucket(self):
        """
        Non-applicable case
        """
        # input params
        event = {}
        whitelist = []
        for item in S3_BUCKET_PERMISSIONS['non_applicable']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_read_all_fails(self):
        """
        read_all_fails case
        """
        # input params
        event = {}
        whitelist = []
        for item in S3_BUCKET_PERMISSIONS['read_all_fails']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_write_all_fails(self):
        """
        write_all_fails case
        """
        # input params
        event = {}
        whitelist = []
        for item in S3_BUCKET_PERMISSIONS['write_all_fails']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)

    def test_evaluate_open_access_fails(self):
        """
        ropen_access_fails case
        """
        # input params
        event = {}
        whitelist = []
        for item in S3_BUCKET_PERMISSIONS['open_access_fails']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_passed_status_assertions(item, output)


class TestS3BucketReadAll(TestS3BucketPermissionsMixin, TestCaseWithAttrAssert):

    def setUp(self):
        """
        """
        super(TestS3BucketReadAll, self).setUpClass()
        self.subclass = S3BucketReadAll(self.app)

    def test_evaluate_read_all_fails(self):
        """
        overwritten ead_all_fails case to fail
        """
        # input params
        event = {}
        whitelist = []
        for item in S3_BUCKET_PERMISSIONS['read_all_fails']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)


class TestS3BucketOpenAccess(TestS3BucketPermissionsMixin, TestCaseWithAttrAssert):

    def setUp(self):
        """
        """
        super(TestS3BucketOpenAccess, self).setUpClass()
        self.subclass = S3BucketOpenAccess(self.app)

    def test_evaluate_open_access_fails(self):
        """
        overwritten open_access_fails case to fail
        """
        # input params
        event = {}
        whitelist = []
        for item in S3_BUCKET_PERMISSIONS['open_access_fails']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)


class TestS3BucketWriteAll(TestS3BucketPermissionsMixin, TestCaseWithAttrAssert):

    def setUp(self):
        """
        """
        super(TestS3BucketWriteAll, self).setUpClass()
        self.subclass = S3BucketWriteAll(self.app)

    def test_evaluate_write_all_fails(self):
        """
        overwritten open_access_fails case to fail
        """
        # input params
        event = {}
        whitelist = []
        for item in S3_BUCKET_PERMISSIONS['write_all_fails']['flaggedResources']:
            # tests
            output = self._evaluate_invariant_assertions(event, item, whitelist)
            self._evaluate_failed_status_assertions(item, output)
