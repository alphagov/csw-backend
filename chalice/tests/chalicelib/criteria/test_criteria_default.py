"""
TestCaseWithAttrAssert subclass of TestCase with new assertion,
CriteriaDefault unit tests and Mixin for all its subclasses TestCases
"""

import importlib
import unittest

from chalice import Chalice
from tests.chalicelib.criteria.test_data import EMPTY_SUMMARY
from chalicelib.criteria.criteria_default import CriteriaDefault


class TestCaseWithAttrAssert(unittest.TestCase):
    """
    TestCase subclass implementing a new assertion method for class attributes
    """

    def assertHasAttr(self, obj, attr, msg=None):
        """
        custom assertion method for hasattr built-in function
        """
        if msg is None:
            msg = "'{}' object has no attribute '{}'".format(obj, attr)
        self.assertTrue(hasattr(obj, attr), msg=msg)


class TestCriteriaDefault(TestCaseWithAttrAssert):
    """
    Unit tests for the CriteriaDefault class
    """

    @classmethod
    def setUpClass(cls):
        """
        initialise the the Chalice app objects once to reuse it in every test
        """
        cls.app = Chalice("test_app")

    def setUp(self):
        """
        initialise the class before every test
        """
        self.criteria_default = CriteriaDefault(self.app)

    def test_init_success(self):
        """
        test that initialization works
        """
        self.assertIsInstance(self.criteria_default, CriteriaDefault)

    def test_init_failure(self):
        """
        test that not passing Chalice app object raises a type error
        """
        self.assertRaises(TypeError, CriteriaDefault)

    def test_init_state(self):
        """
        test that all instance variables have the expected initial values
        """
        # dynamically importing dependancies from the file tested
        gds_aws_client_class = getattr(
            importlib.import_module("chalicelib.aws.gds_aws_client"), "GdsAwsClient"
        )
        # vars initialized with constants on class definition
        with self.subTest():
            self.assertFalse(self.criteria_default.active)
        with self.subTest():
            self.assertDictEqual(self.criteria_default.resources, {})
        with self.subTest():
            self.assertSequenceEqual(self.criteria_default.resource_type, "AWS::*::*")
        with self.subTest():
            self.assertSequenceEqual(self.criteria_default.annotation, "")
        with self.subTest():
            self.assertEqual(self.criteria_default.ClientClass, gds_aws_client_class)
        with self.subTest():
            self.assertIsNone(self.criteria_default.title)
        with self.subTest():
            self.assertIsNone(self.criteria_default.description)
        with self.subTest():
            self.assertIsNone(self.criteria_default.why_is_it_important)
        with self.subTest():
            self.assertIsNone(self.criteria_default.how_do_i_fix_it)
        # vars initialized algorithmically at object instantiation
        with self.subTest():
            self.assertIsInstance(self.criteria_default.app, Chalice)
        with self.subTest():
            self.assertIsInstance(self.criteria_default.client, gds_aws_client_class)

    def test_get_session(self):
        """
        test the get_session method for success and failure
        """
        self.assertFalse(self.criteria_default.get_session())
        # TODO: find account/role params to test for success returning a string

    def test_describe(self):
        """
        test the describe method for success and failure
        """
        describe = self.criteria_default.describe()
        with self.subTest():
            self.assertIsInstance(describe, dict)
        keys = ["title", "description", "why_is_it_important", "how_do_i_fix_it"]
        for key in describe:
            with self.subTest(key=key):
                self.assertIn(key, keys)

    def test_get_data(self):
        """
        test the get_data method for output for any input
        """
        self.assertEqual(self.criteria_default.get_data("any_input"), [])

    def test_build_evaluation(self):
        """
        black box test of the build_evaluation method
        """
        # mock input params
        resource_id = "any_string"
        compliance_type = "COMPLIANT"
        event = {}
        resource_type = self.criteria_default.resource_type
        built_evaluation = self.criteria_default.build_evaluation(
            resource_id, compliance_type, event, resource_type
        )
        with self.subTest():
            self.assertIsInstance(built_evaluation, dict)
        keys = [
            "resource_type",
            "resource_id",
            "compliance_type",
            "is_compliant",
            "is_applicable",
            "status_id",
        ]
        for key in built_evaluation:
            with self.subTest(key=key):
                self.assertIn(key, keys)
        # recall the method with the annotation optional param
        annotation = "optional_string"
        built_evaluation = self.criteria_default.build_evaluation(
            resource_id, compliance_type, event, resource_type, annotation
        )
        with self.subTest():
            self.assertIsInstance(built_evaluation, dict)
        with self.subTest():
            self.assertIn("annotation", built_evaluation)
        # return values tests for type correctness and values when possible
        with self.subTest():
            self.assertEqual(built_evaluation["annotation"], annotation)
        with self.subTest():
            self.assertEqual(built_evaluation["resource_type"], resource_type)
        with self.subTest():
            self.assertEqual(built_evaluation["resource_id"], resource_id)
        with self.subTest():
            self.assertEqual(built_evaluation["compliance_type"], compliance_type)
        with self.subTest():
            self.assertTrue(built_evaluation["is_compliant"])
        with self.subTest():
            self.assertTrue(built_evaluation["is_applicable"])
        with self.subTest():
            self.assertEqual(
                built_evaluation["status_id"],
                self.criteria_default.get_status(built_evaluation),
            )
        # finally the remaining cases of compliance_type
        compliance_type = "NON_COMPLIANT"
        built_evaluation = self.criteria_default.build_evaluation(
            resource_id, compliance_type, event, resource_type, annotation
        )
        with self.subTest():
            self.assertFalse(built_evaluation["is_compliant"])
        with self.subTest():
            self.assertTrue(built_evaluation["is_applicable"])
        with self.subTest():
            self.assertEqual(
                built_evaluation["status_id"],
                self.criteria_default.get_status(built_evaluation),
            )
        compliance_type = "NOT_APPLICABLE"
        built_evaluation = self.criteria_default.build_evaluation(
            resource_id, compliance_type, event, resource_type, annotation
        )
        with self.subTest():
            self.assertFalse(built_evaluation["is_compliant"])
        with self.subTest():
            self.assertFalse(built_evaluation["is_applicable"])
        with self.subTest():
            self.assertEqual(
                built_evaluation["status_id"],
                self.criteria_default.get_status(built_evaluation),
            )

    def test_get_status(self):
        """
        black box test for the get_status method
        """
        eval_dicts = [
            {"is_compliant": False, "is_applicable": False},
            {"is_compliant": False, "is_applicable": True},
            {"is_compliant": True, "is_applicable": False},
            {"is_compliant": True, "is_applicable": True},
        ]
        # test for return of 2 implying a
        with self.subTest():
            self.assertEqual(self.criteria_default.get_status(eval_dicts[0]), 2)
        with self.subTest():
            self.assertEqual(self.criteria_default.get_status(eval_dicts[2]), 2)
        with self.subTest():
            self.assertEqual(self.criteria_default.get_status(eval_dicts[3]), 2)
        # test for fail which returns 3
        with self.subTest():
            self.assertEqual(self.criteria_default.get_status(eval_dicts[1]), 3)

    def test_empty_summary(self):
        """
        test the empty_summary method
        """
        with self.subTest():
            self.assertEqual(
                self.criteria_default.empty_summary(),
                EMPTY_SUMMARY,
                msg="empty summary does not match the prototype",
            )


class CriteriaSubclassTestCaseMixin(object):
    """
    Unit tests for all CriteriaDefault subclasses
    """

    @classmethod
    def setUpClass(cls):
        """
        initialise the the Chalice app objects once to reuse it in every test.
        """
        cls.app = Chalice("test_app")
        cls.test_data = None  # you must load the appropriate test data

    def test_init_state(self):
        """
        test that all instance variables have the expected initial values
        """
        with self.subTest():
            # Checks do not have to be active but value should be set and boolean
            #    self.assertTrue(self.subclass.active, msg="active must be True")
            self.assertIn(self.subclass.active, [True,False], msg="active must be set and boolean")
        with self.subTest():
            self.assertNotEqual(
                self.subclass.resource_type,
                "AWS::*::*",
                msg="declare the correct resource type",
            )
        with self.subTest():
            self.assertSequenceEqual(
                self.subclass.annotation, "", msg="annotation must be empty after init"
            )
        # subclass specific attributes
        # TODO: Ares move this in a TA-specific test case
        # with self.subTest():
        #     self.assertHasAttr(self.subclass, 'check_id')
        #     self.assertIsInstance(
        #         self.subclass.check_id,
        #         str,
        #         msg='check_id must be a non-empty string'
        #     )
        # with self.subTest():
        #     self.assertHasAttr(self.subclass, 'check_id')
        #     self.assertGreater(
        #         len(self.subclass.check_id),
        #         0,
        #         msg='check_id must be a non-empty string'
        #     )
        # with self.subTest():
        #     self.assertHasAttr(self.subclass, 'language')
        #     self.assertIsInstance(
        #         self.subclass.language,
        #         str,
        #         msg='language must be a non-empty string'
        #     )
        # with self.subTest():
        #     self.assertHasAttr(self.subclass, 'language')
        #     self.assertGreater(
        #         len(self.subclass.language),
        #         0,
        #         msg='language must be a non-empty string'
        #     )
        # with self.subTest():
        #     self.assertHasAttr(self.subclass, 'region')
        #     self.assertIsInstance(
        #         self.subclass.region,
        #         str,
        #         msg='region must be a non-empty string'
        #     )
        # with self.subTest():
        #     self.assertHasAttr(self.subclass, 'region')
        #     self.assertGreater(
        #         len(self.subclass.region),
        #         0,
        #         msg='region must be a non-empty string'
        #     )
        with self.subTest():
            self.assertIsInstance(
                self.subclass.title, str, msg="title must be a non-empty string"
            )
            self.assertGreater(
                len(self.subclass.title), 0, msg="title must be a non-empty string"
            )
        with self.subTest():
            self.assertIsInstance(
                self.subclass.description,
                str,
                msg="description must be a non-empty string",
            )
            self.assertGreater(
                len(self.subclass.description),
                0,
                msg="description must be a non-empty string",
            )
        with self.subTest():
            self.assertIsInstance(
                self.subclass.why_is_it_important,
                str,
                msg="why_is_it_important must be a non-empty string",
            )
            self.assertGreater(
                len(self.subclass.why_is_it_important),
                0,
                msg="why_is_it_important must be a non-empty string",
            )
        with self.subTest():
            self.assertIsInstance(
                self.subclass.how_do_i_fix_it,
                str,
                msg="how_do_i_fix_it must be a non-empty string",
            )
            self.assertGreater(
                len(self.subclass.how_do_i_fix_it),
                0,
                msg="how_do_i_fix_it must be a non-empty string",
            )

    def test_translate(self):
        """
        get_data method tests
        """
        # input params
        data = {}
        # output value
        output = self.subclass.translate(data)
        with self.subTest():
            self.assertIsInstance(
                output, dict, msg="the get_data method must return a dictionary"
            )
        with self.subTest():
            self.assertIn(
                "resource_id",
                output,
                msg="""
                    the get_data method must return
                    a dictionary with a key named resource_id
                """,
            )
        with self.subTest():
            self.assertIsInstance(
                output["resource_id"],
                str,
                msg="""
                    the get_data method must return a dictionary
                    with a key named resource_id that has a string value
                """,
            )
        with self.subTest():
            self.assertIn(
                "resource_name",
                output,
                msg="""
                    the get_data method must return
                    a dictionary with a key named resource_name
                """,
            )
        with self.subTest():
            self.assertIsInstance(
                output["resource_name"],
                str,
                msg="""
                    the get_data method must return a dictionary
                    with a key named resource_name that has a string value
                """,
            )

    def _evaluate_invariant_assertions(self, event, item, whitelist):
        """
        tests for invariants of all input combos
        must be called by all black box tests of the evaluate method
        it returns the result of evaluate, independent of the tests' results
        """
        init_resource_type = self.subclass.resource_type
        # output values
        output = self.subclass.evaluate(event, item, whitelist)
        # tests
        with self.subTest():
            self.assertIsInstance(
                output, dict, msg="evaluate did not return a dictionary"
            )
        eval_keys = [
            "resource_type",
            "resource_id",
            "compliance_type",
            "is_compliant",
            "is_applicable",
            "status_id",
        ]
        for key in eval_keys:
            with self.subTest(key=key):
                self.assertIn(
                    key, output, msg="%s is not in the returned dictionary's keys" % key
                )
        with self.subTest():
            self.assertEqual(
                self.subclass.resource_type,
                init_resource_type,
                msg="evaluate must not change the resource_type",
            )
        return output

    def _evaluate_inapplicable_status_assertions(self, item, output):
        """
        green (status: ok) test
        """
        # ignored tests
        with self.subTest():
            self.assertNotIn(
                "annotation",
                output,
                msg="evaluate must not return an annotation when not applicable",
            )
        with self.subTest():
            self.assertEqual(
                self.subclass.annotation,
                "",
                msg="the object's annotation must be an blank string",
            )
        with self.subTest():
            self.assertFalse(output["is_compliant"])
        with self.subTest():
            self.assertFalse(output["is_applicable"])
        with self.subTest():
            self.assertEqual(output["status_id"], 2)

    def _evaluate_passed_status_assertions(self, item, output):
        """
        green (status: ok) test
        """
        # green tests
        with self.subTest():
            self.assertNotIn(
                "annotation",
                output,
                msg="evaluate must not return an annotation when successful",
            )
        with self.subTest():
            self.assertEqual(
                self.subclass.annotation,
                "",
                msg="the object's annotation must be an blank string",
            )
        with self.subTest():
            self.assertTrue(output["is_compliant"])
        with self.subTest():
            self.assertTrue(output["is_applicable"])
        with self.subTest():
            self.assertEqual(output["status_id"], 2)

    def _evaluate_failed_status_assertions(self, item, output):
        """
        yellow/red tests
        """
        # test the status variables
        with self.subTest():
            self.assertFalse(output["is_compliant"])
        with self.subTest():
            self.assertTrue(output["is_applicable"])
        with self.subTest():
            self.assertEqual(output["status_id"], 3)
        # test that the instances annotation contains all necessary info
        msg = "evaluate must have an annotation key with value a string"
        with self.subTest():
            self.assertIn("annotation", output, msg=msg)
        with self.subTest():
            self.assertIsInstance(self.subclass.annotation, str, msg=msg)


if __name__ == "__main__":
    unittest.main()
