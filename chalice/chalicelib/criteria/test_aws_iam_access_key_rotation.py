import unittest

from chalice import Chalice
from chalicelib.criteria.aws_iam_access_key_rotation import (
    AwsIamAccessKeyRotation
)
from chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from chalicelib.criteria.test_data import IAM_KEY_ROTATION_ITEMS


class TestAwsIamAccessKeyRotation(
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
):
    """
    Unit tests for the CriteriaDefault class
    """

    @classmethod
    def setUpClass(cls):
        """
        initialise the the Chalice app objects once to reuse it in every test.
        """
        super(TestAwsIamAccessKeyRotation, cls).setUpClass()
        cls.test_data = IAM_KEY_ROTATION_ITEMS

    def setUp(self):
        """
        """
        self.subclass = AwsIamAccessKeyRotation(self.app)

    def test_init_success(self):
        """
        test that initialization works
        """
        self.assertIsInstance(
            self.subclass, AwsIamAccessKeyRotation
        )

    def test_init_failure(self):
        """
        test that not passing Chalice app object raises a type error
        """
        self.assertRaises(TypeError, AwsIamAccessKeyRotation)

    def test_init_client(self):
        """
        test that all instance variables have the expected initial values
        """
        #TODO: dynamically importing dependancies from the file tested
        self.fail('import or write the appropriate client')

    def test_get_data(self):
        """
        """
        # input params
        session = None
        kwargs = {}  # None
        # output value
        item = self.subclass.get_data(session, **kwargs)
        # must return a dictionary with the three necessary keys
        msg = "the method must return a dictionary with ['result']['status']"
        self.assertIsInstance(item, dict, msg=msg)
        self.assertIsInstance(
            item['result']['status'],
            dict,
            msg=msg
        )

    def test_evaluate_yellow(self):
        """
        yellow (status: warning) test
        """
        # input params
        event = {}
        item = self.test_data['yellow']
        whitelist = []
        # tests
        output = self._evaluate_invariant_assertions(event, item, whitelist)
        self._evaluate_failed_status_assertions(item, output)
        # extract the metadata of flaggedResources
        metadata = [
            flagged['metadata']
            for flagged in item['result']['flaggedResources']
            if flagged['status'] == 'warning'
        ]
        with self.subTest():
            self.assertGreater(len(metadata), 0, msg='no warnings captured')
        msg_stubs = [None, 'name', 'key', None, 'reason']
        for record in metadata:
            for i, key in enumerate(record):
                if i in [1, 2, 4]:  # check only for name, key and reason
                    with self.subTest(key=key):
                        self.assertIn(
                            key,
                            self.subclass.annotation,
                            msg='{} is missing from the annotation'.format(
                                msg_stubs[i]
                            )
                        )

    def test_evaluate_red(self):
        """
        red (status: error) test
        """
        # input params
        event = {}
        item = self.test_data['red']
        whitelist = []
        # first test the invariants and get the evaluate method's output
        output = self._evaluate_invariant_assertions(event, item, whitelist)
        self._evaluate_failed_status_assertions(item, output)
        # extract the metadata of flaggedResources
        metadata = [
            flagged['metadata']
            for flagged in item['result']['flaggedResources']
            if flagged['status'] == 'error'
        ]
        with self.subTest():
            self.assertGreater(len(metadata), 0, msg='no errors captured')
        msg_stubs = [None, 'name', 'key', None, 'reason']
        for record in metadata:
            for i, key in enumerate(record):
                if i in [1, 2, 4]:  # check only for name, key and reason
                    with self.subTest(key=key):
                        self.assertIn(
                            key,
                            self.subclass.annotation,
                            msg='{} is missing from the annotation'.format(
                                msg_stubs[i]
                            )
                        )


if __name__ == '__main__':
    unittest.main()
