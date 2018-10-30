import unittest

from chalice import Chalice
from chalicelib.criteria.aws_iam_access_key_rotation import (
    AwsIamAccessKeyRotation
)
from chalicelib.criteria.test_criteria_default import (
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
)


class TestAwsIamAccessKeyRotation(
    CriteriaSubclassTestCaseMixin, TestCaseWithAttrAssert
):
    """
    Unit tests for the CriteriaDefault class
    """

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


if __name__ == '__main__':
    unittest.main()
