from chalicelib.criteria.aws_kms_managed_cmk_rotation import ManagedCmkRotation

from tests.chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)
from tests.chalicelib.criteria.test_data import MANAGED_CMK_ROTATION


class TestManagedCmkRotation(CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert):

    @classmethod
    def setUpClass(cls):
        super(TestManagedCmkRotation, cls).setUpClass()
        cls.test_data = MANAGED_CMK_ROTATION

    def setUp(self):
        """
        """
        super(TestManagedCmkRotation, self).setUp()
        self.subclass = ManagedCmkRotation(self.app)

    def test_init_client(self):
        self.assertIn('get_key_list_with_details', dir(self.subclass.client))

    def test_translate(self):
        translation = self.subclass.translate(self.test_data['fail'])
        with self.subTest():
            self.assertIsInstance(
                translation, dict, 
                msg="The output of the translate method should be a dict"
            )
        with self.subTest():
            self.assertIn(
                "region", translation, 
                msg="The key 'region' was not in the output of the translate method."
            )
            self.assertIsInstance(
                translation['region'], str,
                msg="The value of 'region' must be a non-empty string"
            )
            self.assertGreater(
                len(translation['region']), 0,
                msg="The value of 'region' must be a non-empty string"
            )
        with self.subTest():
            self.assertIn(
                "resource_id", translation, 
                msg="The key 'resource_id' was not in the output of the translate method."
            )
            self.assertIsInstance(
                translation['resource_id'], str,
                msg="The value of 'resource_id' must be a non-empty string"
            )
            self.assertGreater(
                len(translation['resource_id']), 0,
                msg="The value of 'resource_id' must be a non-empty string"
            )
        with self.subTest():
            self.assertIn(
                "resource_name", translation, 
                msg="The key 'resource_name' was not in the output of the translate method."
            )
            self.assertIsInstance(
                translation['resource_name'], str,
                msg="The value of 'resource_name' must be a non-empty string"
            )
            self.assertGreater(
                len(translation['resource_name']), 0,
                msg="The value of 'resource_name' must be a non-empty string"
            )

    def test_evaluate(self):
        for key in self.test_data:
            with self.subTest(key=key):
                output = self._evaluate_invariant_assertions({}, self.test_data[key], [])
                if key == 'fail':
                    self._evaluate_failed_status_assertions(self.test_data['fail'], output)
                else:
                    self._evaluate_passed_status_assertions(self.test_data[key], output)
