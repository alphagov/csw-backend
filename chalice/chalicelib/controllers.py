import datetime
import cerberus
import json
import re
from chalicelib import models
from app import app
from chalicelib.validators import FormValidator


class FormController:
    """
    Implements the validation from "application/x-www-form-urlencoded"
    post data using cerberus with some custom rules

    The encoded post data is submitted as arrays for some reason so
    the parse_post_data method strips that into a simpler data model

    This is basically like an API controller but because we don't have
    a REST verb we've got a mode field in the form which sets the verb
    """

    # Cerberus example implementation
    # schema = {'name': {'type': 'string'}, 'age': {'type': 'integer', 'min': 10}}
    # document = {'name': 'Little Joe', 'age': 5}
    # v.validate(document, schema)
    schema = {}
    item = {}
    data = None
    mode = None
    processed_status = {}

    def __init__(self):
        self.form_validator = FormValidator()

    def set_post_data(self, data):
        self.post_data = data

    def get_mode(self):
        self.mode = self.post_data["mode"][0]
        return self.mode

    def get_item_id(self):
        self.item_id = int(self.post_data["id"][0])
        return self.item_id

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

    def get_date_from_components(self, components):

        expiry_date = datetime.date(
            int(self.data[components]["year"]),
            int(self.data[components]["month"]),
            int(self.data[components]["day"]),
        )

        date_field = datetime.datetime.combine(
            expiry_date, datetime.datetime.min.time()
        )
        return date_field

    def process(self):
        mode = self.get_mode()
        output = {}
        try:
            if mode == "load":
                output = self.process_load()
            elif mode == "create":
                output = self.process_create()
            elif mode == "update":
                output = self.process_update()
            elif mode == "expire":
                output = self.process_expire()
            elif mode == "activate":
                output = self.process_active(True)
            elif mode == "deactivate":
                output = self.process_active(False)
            else:
                app.log.error(f"Form process mode: {mode} not recognised")
                output = self.data
                self.processed_status = {
                    "success": False,
                    "message": f"Form requested action ({mode}) not recognised",
                }

        except Exception:
            message = app.utilities.get_typed_exception()
            self.processed_status = {
                "success": False,
                "message": f"Form {mode} failed: {message}",
            }

        return output

    def set_user(self, user):
        self.user = user

    def set_item(self, id):
        self.item = self._Model.get_by_id(id)

    def build_model(self):
        return self._Model.clean(self.data)

    def process_load(self):
        self.item = self._Model.get_by_id(self.get_item_id())
        self.processed_status = {
            "success": True,
            "message": f"The entry can be edited in the form below",
        }
        return self.item

    def process_create(self):
        is_valid = self.validate(self.post_data)

        model_data = self.build_model()
        if is_valid:
            self.item = self._Model.create(**model_data)
            self.processed_status = {
                "success": True,
                "message": "The record was created successfully",
            }
        else:
            self.item = model_data
            self.processed_status = {
                "success": False,
                "message": "The record was not created successfully",
            }

        return self.item

    def process_update(self):

        is_valid = self.validate(self.post_data)
        model_data = self.build_model()
        if is_valid:
            self.item = self._Model.get_by_id(self.get_item_id())
            for field, value in model_data.items():
                setattr(self.item, field, value)
            self.item.save()
            self.processed_status = {
                "success": True,
                "message": "The record was updated successfully",
            }
        else:
            self.item = model_data
            self.processed_status = {
                "success": False,
                "message": "The record was not updated successfully",
            }
        return self.item

    def process_expire(self):
        now = datetime.datetime.now()
        self.item = self._Model.get_by_id(self.get_item_id())
        self.item.date_expires = now
        self.item.save()
        self.processed_status = {
            "success": True,
            "message": "The record was set to expired",
        }
        return self.item

    def process_active(self, state):
        self.item = self._Model.get_by_id(self.get_item_id())
        self.item.active = state
        self.item.save()
        status = "Active" if state else "Inactive"
        self.processed_status = {
            "success": True,
            "message": f"The record state was set to :{status}",
        }
        return self.item

    def convert_model_to_dict(self, item):
        # turn model instance into a dict using .raw if necessary
        if type(item) is dict:
            item_data = item
            app.log.debug("Model item is already a dict")
        else:
            app.log.debug("Convert item model to dict from " + str(type(item)))
            item_data = item.raw()
        return item_data

    def append_form_fields(self, item):
        return self.convert_model_to_dict(item)


class FormControllerAddResourceException(FormController):

    _Model = models.ResourceException
    schema = {
        "resource_persistent_id": {"type": "string"},
        "criterion_id": {"type": "integer"},
        "account_subscription_id": {"type": "integer"},
        "reason": {
            "type": "string",
            "notnull": True,
            "maxlength": 500,
            "errorpattern": "([^A-Z0-9\s'\_\-\.\?\\\/]+)",
        },
        "expiry_components": {"type": "dict", "datecomponents": True},
        "expiry_date": {
            "coerce": "datecomponents",
            "datemin": (datetime.timedelta(days=0).total_seconds()),
            "datemax": (datetime.timedelta(days=365).total_seconds()),
        },
    }

    def parse_post_data(self, data):

        try:
            now = datetime.datetime.now()
            expiry_date = {
                "year": int(data.get("exception-expiry-year", [now.year])[0]),
                "month": int(data.get("exception-expiry-month", [now.month])[0]),
                "day": int(data.get("exception-expiry-day", [now.day])[0]),
            }

            document = {}
            document["resource_persistent_id"] = data["resource_persistent_id"][0]
            document["criterion_id"] = int(data["criterion_id"][0])
            document["account_subscription_id"] = int(
                data["account_subscription_id"][0]
            )
            document["reason"] = self.flatten_text_input(
                data.get("exception-reason", [])
            )
            document["expiry_components"] = expiry_date
            document["expiry_date"] = expiry_date

            app.log.debug(json.dumps(document))
        except Exception:
            app.log.error(
                "Failed to parse post data" + app.utilities.get_typed_exception()
            )
        return document

    def get_model_defaults(self, **kwargs):
        # exception = self._Model.get_defaults(kwargs["account_subscription_id"], self.user.id)
        exception = self._Model.find_exception(
            kwargs["criterion_id"],
            kwargs["resource_persistent_id"],
            kwargs["account_subscription_id"],
        )
        return exception

    def build_model(self):
        exception = self.get_model_defaults(
            criterion_id=self.data["criterion_id"],
            resource_persistent_id=self.data["resource_persistent_id"],
            account_subscription_id=self.data["account_subscription_id"],
        )

        exception["date_expires"] = self.get_date_from_components("expiry_components")
        exception["reason"] = self.data["reason"]
        exception["user_id"] = self.user.id
        exception_data = self._Model.clean(exception)
        return exception_data

    def append_form_fields(self, item):
        # turn model instance into a dict using .raw if necessary
        item_data = super(FormControllerAddResourceException, self).append_form_fields(
            item
        )

        app.log.debug("item_data is an instance of " + str(type(item_data)))
        if self.data and self.data["expiry_components"]:
            item_data["expiry_day"] = self.data["expiry_components"]["day"]
            item_data["expiry_month"] = self.data["expiry_components"]["month"]
            item_data["expiry_year"] = self.data["expiry_components"]["year"]
        else:
            item_data["expiry_day"] = item_data["date_expires"].day
            item_data["expiry_month"] = item_data["date_expires"].month
            item_data["expiry_year"] = item_data["date_expires"].year

        return item_data


class FormControllerAddAllowListException(FormController):

    _Model = models.AccountSshCidrAllowlist
    schema = {
        "mode": {"type": "string"},
        "id": {"type": "integer"},
        "account_subscription_id": {"type": "integer"},
        "cidr": {
            "type": "string",
            "notnull": True,
            "maxlength": 20,
            "matchpattern": "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}",
        },
        "reason": {
            "type": "string",
            "notnull": True,
            "maxlength": 500,
            "errorpattern": "([^A-Z0-9\s'\_\-\.\?\\\/]+)",
        },
        "expiry_components": {"type": "dict", "datecomponents": True},
        "expiry_date": {
            "coerce": "datecomponents",
            "datemin": (datetime.timedelta(days=0).total_seconds()),
            "datemax": (datetime.timedelta(days=365).total_seconds()),
        },
    }

    def parse_post_data(self, data):

        try:
            now = datetime.datetime.now()
            expiry_date = {
                "year": int(data.get("exception-expiry-year", [now.year])[0]),
                "month": int(data.get("exception-expiry-month", [now.month])[0]),
                "day": int(data.get("exception-expiry-day", [now.day])[0]),
            }

            document = {}
            document["mode"] = data["mode"][0]
            document["id"] = int(data["id"][0])
            document["account_subscription_id"] = int(
                data["account_subscription_id"][0]
            )
            document["cidr"] = self.flatten_text_input(data.get("exception-cidr", []))
            document["reason"] = self.flatten_text_input(
                data.get("exception-reason", [])
            )
            document["expiry_components"] = expiry_date
            document["expiry_date"] = expiry_date

            app.log.debug(json.dumps(document))
        except Exception:
            app.log.error(
                "Failed to parse post data: " + app.utilities.get_typed_exception()
            )
        return document

    def get_model_defaults(self, **kwargs):
        exception = self._Model.get_defaults(
            kwargs["account_subscription_id"], self.user.id
        )
        return exception

    def build_model(self):
        exception = self._Model.get_defaults(
            self.data["account_subscription_id"], self.user.id
        )

        exception["date_expires"] = self.get_date_from_components("expiry_components")
        exception["reason"] = self.data["reason"]
        exception["cidr"] = self.data["cidr"]
        exception["user_id"] = self.user.id
        exception_data = self._Model.clean(exception)
        return exception_data

    def append_form_fields(self, item):
        # turn model instance into a dict using .raw if necessary
        item_data = super(FormControllerAddAllowListException, self).append_form_fields(
            item
        )

        if self.data and self.data["expiry_components"]:
            item_data["expiry_day"] = self.data["expiry_components"]["day"]
            item_data["expiry_month"] = self.data["expiry_components"]["month"]
            item_data["expiry_year"] = self.data["expiry_components"]["year"]
        else:
            item_data["expiry_day"] = item_data["date_expires"].day
            item_data["expiry_month"] = item_data["date_expires"].month
            item_data["expiry_year"] = item_data["date_expires"].year

        app.log.debug(app.utilities.to_json(item_data))
        return item_data

    def get_allowlist(self, account_subscription_id):
        now = datetime.datetime.now()
        allowlist = self._Model.select().where(
            self._Model.account_subscription_id == account_subscription_id,
            self._Model.date_expires > now,
        )
        allowed = []
        for item in allowlist:
            allowed.append(item.serialize())

        return allowed
