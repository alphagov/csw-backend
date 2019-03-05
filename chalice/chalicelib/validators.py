import datetime
import cerberus
import json
import re
from app import app

class Form():
    """
    Implements the validation from "application/x-www-form-urlencoded"
    post data using cerberus with some custom rules

    The encoded post data is submitted as arrays for some reason so
    the parse_post_data method strips that into a simpler data model
    """
    # Cerberus example implementation
    # schema = {'name': {'type': 'string'}, 'age': {'type': 'integer', 'min': 10}}
    # document = {'name': 'Little Joe', 'age': 5}
    # v.validate(document, schema)
    schema = {}
    def __init__(self):
        self.form_validator = FormValidator()

    def parse_post_data(self, data):
        """
        Remove unnecessary array indices from the post data
        :param data:
        :return:
        """
        document = {}
        return document

    def flatten_text_input(self, field):
        return re.sub("\s+", " ", " ".join(field))

    def validate(self, post_data):
        """
        Call the cerberus validator against the self.schema
        :param post_data:
        :return:
        """
        self.data = self.parse_post_data(post_data)
        return self.form_validator.validate(self.data, self.schema)

    def get_errors(self):
        return self.form_validator.errors

class FormAddResourceException(Form):

    schema = {
        "resource_persistent_id": {"type": "string"},
        "criterion_id": {"type": "integer"},
        "account_subscription_id": {"type": "integer"},
        "reason": {
            "type": "string",
            "notnull": True,
            "maxlength": 500,
            "errorpattern": "([^A-Z0-9\s\'\_\-\.\?\\\/]+)"
        },
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

    def parse_post_data(self, data):

        try:
            now = datetime.datetime.now()
            expiry_date = {
                "year": int(data.get('exception-expiry-year',[now.year])[0]),
                "month": int(data.get('exception-expiry-month',[now.month])[0]),
                "day": int(data.get('exception-expiry-day',[now.day])[0])
            }

            document = {}
            document["resource_persistent_id"] = data["resource_persistent_id"][0]
            document["criterion_id"] = int(data["criterion_id"][0])
            document["account_subscription_id"] = int(data["account_subscription_id"][0])
            document["reason"] = self.flatten_text_input(data.get("exception-reason",[]))
            document["expiry_components"] = expiry_date
            document["expiry_date"] = expiry_date

            app.log.debug(json.dumps(document))
        except Exception as err:
            app.log.error("Failed to parse post data" + app.utilities.get_typed_exception(err))
        return document



class FormAddAllowListException(Form):

    schema = {
        "criterion_id": {"type": "integer"},
        "account_subscription_id": {"type": "integer"},
        "values": {
            "type": "list",
            "minlength": 1,
            "required": True,
            "schema": {
                "type": "string",
                "notnull": True,
                "maxlength": 500,
                "errorpattern": ""
            }
        },
        "reason": {
            "type": "string",
            "notnull": True,
            "maxlength": 500,
            "errorpattern": "([^A-Z0-9\s\'\_\-\.\?\\\/]+)"
        },
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

    def set_value_pattern(self, pattern):
        self.schema["values"]["schema"]["errorpattern"] = pattern

    def parse_post_data(self, data):

        try:
            now = datetime.datetime.now()
            expiry_date = {
                "year": int(data.get('exception-expiry-year',[now.year])[0]),
                "month": int(data.get('exception-expiry-month',[now.month])[0]),
                "day": int(data.get('exception-expiry-day',[now.day])[0])
            }

            document = {}
            document["criterion_id"] = int(data["criterion_id"][0])
            document["account_subscription_id"] = int(data["account_subscription_id"][0])
            document["values"] = data.get("exception-values", [])
            document["reason"] = self.flatten_text_input(data.get("exception-reason",[]))
            document["expiry_components"] = expiry_date
            document["expiry_date"] = expiry_date

            app.log.debug(json.dumps(document))
        except Exception as err:
            app.log.error("Failed to parse post data" + app.utilities.get_typed_exception(err))
        return document


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
                int(value['year']),
                int(value['month']),
                int(value['day'])
            )
            expiry_timestamp = datetime.datetime.combine(expiry_date, datetime.datetime.min.time())
            # timestamp = expiry_timestamp.isoformat()

        except Exception as err:
            self._error(field, "The date entered is not valid")

    def _normalize_coerce_json(self, value):
        return json.dumps(value)

    def _normalize_coerce_datecomponents(self, value):
        try:
            expiry_date = datetime.date(
                int(value['year']),
                int(value['month']),
                int(value['day'])
            )

            component_datetime = datetime.datetime.combine(expiry_date, datetime.datetime.min.time())
            #timestamp = expiry_timestamp.isoformat()
        except Exception as err:
            #timestamp = ""
            component_datetime = datetime.datetime.now()

        return component_datetime

    def _validate_datemin(self, datemin, field, value):
        """ Test that a datetime falls after now + delta
        The rule value should be a timedelta converted to seconds
        eg "datemin": (timedelta(days=-7).total_seconds())

        The rule's arguments are validated against this schema:
        {'type': 'float'}
        """
        #app.log.debug(f"t:{datemin}, f:{field}, v:{value}")

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
                raise ValueError("Value contains invalid characters : " + match.group(1))
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