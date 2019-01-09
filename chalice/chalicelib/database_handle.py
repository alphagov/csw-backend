"""
Module for reusable classes extending and easing chalice and peewee functionality.
"""

import importlib
import inspect
import os
import pkgutil

import peewee
from playhouse import postgres_ext, shortcuts


class DatabaseHandle():

    def __init__(self, app=None):
        self.handle = None
        self.app = app

    def get_env_var(self, var_name):
        try:
            value = os.environ[var_name]
        except Exception:
            value = ""
        return value

    def log(self, type, message):
        if (self.app is not None):
            if (type == 'error'):
                self.app.log.error(message)
            elif (type == 'debug'):
                self.app.log.debug(message)

    def get_handle(self):
        try:
            if self.handle is None:
                db_host = self.get_env_var('CSW_HOST')
                db_port = self.get_env_var('CSW_PORT')
                db_user = self.get_env_var('CSW_USER')
                db_password = self.get_env_var('CSW_PASSWORD')

                self.handle = postgres_ext.PostgresqlExtDatabase(
                    'csw',
                    user=db_user,
                    password=db_password,
                    host=db_host,
                    port=db_port
                )
        except Exception as err:
            self.app.log.error("Error connecting to db: " + str(err))
            self.handle = None
        return self.handle

    def set_credentials(self, user, password):
        # replace database credentials for duration of lambda execution
        os.environ['CSW_USER'] = user
        os.environ['CSW_PASSWORD'] = password
        # reset handle to force reconnect using new creadentials
        self.handle = None

    def execute_commands(self, commands):
        status = True
        try:
            db_host = self.get_env_var('CSW_HOST')
            db_port = self.get_env_var('CSW_PORT')
            db_user = self.get_env_var('CSW_USER')
            db_password = self.get_env_var('CSW_PASSWORD')
            db = postgres_ext.PostgresqlExtDatabase(
                'postgres',
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            db.connect()
            for command in commands:
                status &= db.execute_sql(command)
        except Exception as err:
            self.app.log.error("Failed to execute commands: " + str(err))
            db.rollback()
            status = False
        db.close()
        return status

    def create_tables(self, tables):
        db = self.get_handle()
        try:
            db.connect()
            db.create_tables(
                tables,
                safe=True
            )
            status = True
        except Exception as e:
            if db is not None:
                db.rollback()
            status = False
            self.app.log.debug(str(e))
        db.close()
        return status

    def get_model(self, model_name):
        """
        Returns the class with named after string passed as model_name.
        """
        return self.get_models()[model_name]

    def get_models(self):
        """
        Dynamically parses the chalicelib.models file for all classes inheriting BaseModel (defined below)
        and returns a dictionary with their names as keys and class as their corresponding values.
        """
        return {
            name: cls
            for name, cls in inspect.getmembers(importlib.import_module('chalicelib.models'))
            if inspect.isclass(cls) and BaseModel in cls.mro()
        }

    def create_item(self, event):
        db = self.get_handle()
        try:
            db.connect()
            model = self.get_model(event['Model'])
            item = model.create(**event['Params'])
            db.close()
        except Exception as e:
            if db is not None:
                db.rollback()
            item = None
            self.app.log.debug(str(e))
        return item

    def create_items(self, event):
        db = self.get_handle()
        created = []
        try:
            db.connect()
            for item_data in event['Items']:
                self.app.log.debug(str(item_data))
                model = self.get_model(item_data['Model'])
                item = model.create(**item_data['Params'])
                created.append(item)
            db.close()
        except Exception as e:
            if db is not None:
                db.rollback()
            self.app.log.error(str(e))
        return created

    def get_item(self, event):
        db = self.get_handle()
        db.connect()
        model = self.get_model(event['Model'])
        item = model.get_by_id(event['Id'])
        db.close()

        return item

    def get_or_create_criterion(self, event):
        """
        This will work only on criteria using trusted advisor!!!
        To be generic, the client's API calls must be within one function that each subclass overloads!
        """
        db = self.get_handle()
        db.connect()
        model = self.get_model('Criterion')
        count = model.select().where(model.criterion_name == event['criterion_name']).count()
        db.close()
        if count < 1:
            module = '.'.join(event['criterion_name'].split('.')[:-1])
            cls_name = event['criterion_name'].split('.')[-1]
            obj = getattr(importlib.import_module(module), cls_name)(self.app)
            self.create_item({
                'Model': 'Criterion',
                'Params': {
                    "criterion_name": cls_name,
                    "criteria_provider_id": 2,
                    "invoke_class_name": event['criterion_name'],
                    "invoke_class_get_data_method": "describe_trusted_advisor_check_result",
                    "title":  obj.title,
                    "description": obj.description,
                    "why_is_it_important": obj.why_is_it_important,
                    "how_do_i_fix_it": obj.how_do_i_fix_it,
                    "active": obj.active,
                    "is_regional": False
                },
            })


class BaseModel(peewee.Model):

    def serialize(self):
        """
        Returns a model's instance as a python dictionary.
        """
        # front end does not need user ID here
        data = shortcuts.model_to_dict(self)
        return data

    class Meta:
        database = DatabaseHandle().get_handle()
        schema = "public"

    def save(self, force_insert=False, only=None):
        try:
            item = super().save(force_insert, only)
        except Exception as error:
            item = 0
            self._meta.database.app.log.error("Save failed: "+str(error))
            self._meta.database.rollback()
        return item

    @classmethod
    def create(cls, **query):
        try:
            item = super().create(**query)
        except Exception as error:
            item = None
            cls._meta.database.app.log.error("Create failed: " + str(error))
            cls._meta.database.rollback()
        return item

    @classmethod
    def serialize_list(cls, items):
        return [
            item.serialize() for item in items
        ]

