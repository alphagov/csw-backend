import os
from playhouse.postgres_ext import PostgresqlExtDatabase


class DatabaseHandle():

    handle = None
    models = dict()

    def __init__(self, app=None):
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

                self.handle = PostgresqlExtDatabase(
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

        os.environ['CSW_USER'] = user
        os.environ['CSW_PASSWORD'] = password

    def execute_commands(self, commands):

        db = self.get_handle()
        try:
            db.connect()
            for command in commands:
                db.execute_sql(command)

        except Exception:
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
            print(str(e))

        db.close()

        return status

    def add_model(self, model_name, model_class):
        self.models[model_name] = model_class

    def get_model(self, model_name):

        return self.models[model_name]

    def get_models(self):

        return self.models

    def create_item(self, event):

        db = self.get_handle()
        db.connect()
        model = self.get_model(event['Model'])
        item = model.create(**event['Params'])
        db.close()

        return item

    def get_item(self, event):

        db = self.get_handle()
        db.connect()
        model = self.get_model(event['Model'])
        item = model.get_by_id(event['Id'])
        db.close()

        return item
