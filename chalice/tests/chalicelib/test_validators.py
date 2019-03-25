import unittest
import datetime
import os
import json
from chalicelib.validators import FormValidator

class TestFormValidator(unittest.TestCase):
    """
    Unit tests for the AuthHandler class
    """

    def setUp(self):
        """
        """
        self.now = datetime.datetime.now()
        self.form_validator = FormValidator()

    def test_init_success(self):
        """
        test that initialization works
        """

        self.assertIsInstance(
            self.form_validator, FormValidator
        )

    def test_validate(self):
        now = datetime.datetime.now()
        valid_date_components = {
            "year": now.year,
            "month": now.month,
            "day": now.day
        }
        invalid_date_components = {
            "year": (now.year + 2),
            "month": now.month,
            "day": now.day
        }

        schema = {
            "resource_persistent_id": {"type": "string"},
            "criterion_id": {"type": "integer"},
            "account_subscription_id": {"type": "integer"},
            "reason": {"type": "string"},
            "expiry_components": {
                "type": "dict",
                "datecomponents": True
            },
            "expiry_date": {
                "coerce": "datecomponents",
                "datemin": (datetime.timedelta(days=0).total_seconds()),
                "datemax": (datetime.timedelta(days=365).total_seconds())
            }
        }

        # print(json.dumps(schema))

        document = {
            "expiry_components": valid_date_components,
            "expiry_date": valid_date_components
        }
        is_valid = self.form_validator.validate(document, schema)

        self.assertTrue(is_valid)

        document = {
            "expiry_components": invalid_date_components,
            "expiry_date": invalid_date_components
        }
        is_valid = self.form_validator.validate(document, schema)

        self.assertFalse(is_valid)

    def test_get_target_date(self):

        delta = datetime.timedelta(days=365)

        calc_date = (self.now + delta).isoformat()[0:16]
        target_date = self.form_validator.get_target_date(delta)[0:16]
        print (f"{calc_date} =? {target_date}")
        self.assertTrue(calc_date == target_date)


if __name__ == '__main__':
    unittest.main()
