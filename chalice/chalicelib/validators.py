import datetime
import cerberus
import json
import re
from chalicelib import models
from app import app


class FormValidator(cerberus.Validator):
    def __init__(self):
        self.now = datetime.datetime.now()
        super(FormValidator, self).__init__()

    def get_target_date(self, delta):
        target = (self.now + delta).isoformat()
        return target

    def after_min(self, item, min):
        return item >= (self.now + min)

    def before_max(self, item, max):
        return item <= (self.now + max)

    def get_after_message(self, delta):
        target = self.get_target_date(delta)
        return f"Date must be on or after {target}"

    def get_before_message(self, delta):
        target = self.get_target_date(delta)
        return f"Date must be on or before {target}"

    def _validate_datecomponents(self, datecomponents, field, value):
        """ Test that a dict resolves to a valid date

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        try:

            expiry_date = datetime.date(
                int(value["year"]), int(value["month"]), int(value["day"])
            )
            expiry_timestamp = datetime.datetime.combine(
                expiry_date, datetime.datetime.min.time()
            )
            # timestamp = expiry_timestamp.isoformat()

        except Exception as err:
            self._error(field, "The date entered is not valid")

    def _normalize_coerce_json(self, value):
        return json.dumps(value)

    def _normalize_coerce_datecomponents(self, value):
        try:
            expiry_date = datetime.date(
                int(value["year"]), int(value["month"]), int(value["day"])
            )

            component_datetime = datetime.datetime.combine(
                expiry_date, datetime.datetime.min.time()
            )
            # timestamp = expiry_timestamp.isoformat()
        except Exception as err:
            # timestamp = ""
            component_datetime = datetime.datetime.now()

        return component_datetime

    def _validate_datemin(self, datemin, field, value):
        """ Test that a datetime falls after now + delta
        The rule value should be a timedelta converted to seconds
        eg "datemin": (timedelta(days=-7).total_seconds())

        The rule's arguments are validated against this schema:
        {'type': 'float'}
        """
        # app.log.debug(f"t:{datemin}, f:{field}, v:{value}")

        self.now = datetime.datetime.now()
        delta = datetime.timedelta(seconds=datemin)

        if datemin and not self.after_min(value, delta):
            self._error(field, self.get_after_message(delta))

    def _validate_datemax(self, datemax, field, value):
        """ Test that a datetime falls before now + delta
        The rule value should be a timedelta converted to seconds
        eg "datemax": (timedelta(days=90).total_seconds())

        The rule's arguments are validated against this schema:
        {'type': 'float'}
        """
        self.now = datetime.datetime.now()
        delta = datetime.timedelta(seconds=datemax)

        if datemax and not self.before_max(value, delta):
            self._error(field, self.get_after_message(delta))

    def _validate_matchpattern(self, matchpattern, field, value):
        """ Test that a datetime falls after now + delta

        The rule's arguments are validated against this schema:
        {'type': 'string'}
        """
        try:
            # invalid_chars = "([^A-Z0-9\s\'\_\-\.\?\\\/]+)"
            pattern = re.compile(matchpattern)
            if not pattern.match(value):
                raise ValueError(
                    "Value does not match the CIDR pattern eg 112.123.134.0/24"
                )
        except Exception as err:
            self._error(field, str(err))

    def _validate_errorpattern(self, errorpattern, field, value):
        """ Test that a datetime falls after now + delta

        The rule's arguments are validated against this schema:
        {'type': 'string'}
        """
        try:
            # invalid_chars = "([^A-Z0-9\s\'\_\-\.\?\\\/]+)"
            pattern = re.compile(errorpattern)
            if pattern.match(value):
                match = re.search(errorpattern, value)
                raise ValueError(
                    "Value contains invalid characters : " + match.group(1)
                )
        except Exception as err:
            self._error(field, str(err))

    def _validate_notnull(self, notnull, field, value):
        """ Rewritten empty test for better error message

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        # Check for a non-existent value, empty string and string containing only whitespace
        try:
            if value is None or re.match("^\s*$", value):
                raise ValueError(f"The {field} field cannot be empty")
        except Exception as err:
            self._error(field, str(err))
