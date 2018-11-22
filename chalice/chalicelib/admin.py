"""
DATABASE ADMIN HELPER LAMBDAS
native lambda admin function to be invoked
"""
# TODO add authentication or rely on API permissions and assume roles to control access
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from app import app
from chalicelib.database_handle import DatabaseHandle


@app.lambda_function()
def database_create_tables(event, context):
    try:
        dbh = DatabaseHandle(app)
        table_list = []
        message = ""
        for table_name in event['Tables']:
            model = dbh.get_model(table_name)
            table_list.append(model)
        created = dbh.create_tables(table_list)
    except Exception as err:
        app.log.error(str(err))
        created = False
        message = str(err)
    if created:
        response = ", ".join(event['Tables'])
    else:
        response = f"Table create failed: {message}"
    return response


@app.lambda_function()
def database_create_item(event, context):
    try:
        dbh = DatabaseHandle(app)
        item = dbh.create_item(event)
        data = item.serialize()
        json_data = app.utilities.to_json(data)
    except Exception as err:
        app.log.error(str(err))
        json_data = None
    return json_data


@app.lambda_function()
def database_create_items(event, context):
    try:
        dbh = DatabaseHandle(app)
        created = dbh.create_items(event)
        json_data = app.utilities.to_json(created)
    except Exception as err:
        app.log.error(str(err))
        json_data = None
    return json_data


@app.lambda_function()
def database_get_item(event, context):
    app.log.debug('database_get_item function')
    try:
        dbh = DatabaseHandle(app)
        item = dbh.get_item(event)
        data = item.serialize()
        json_data = app.utilities.to_json(data)
    except Exception as err:
        app.log.error(str(err))
        json_data = None
    return json_data


@app.lambda_function()
def database_run(event, context):
    try:
        dbh = DatabaseHandle(app)
        dbh.set_credentials(event['User'], event['Password'])
        status = dbh.execute_commands(event['Commands'])
    except Exception as err:
        app.log.error(str(err))
        status = False
    return status


@app.lambda_function()
def database_list_models(event, context):
    try:
        dbh = DatabaseHandle(app)
        models = dbh.get_models()
        tables = models.keys()
    except Exception as err:
        app.log.error(str(err))
        tables = []
    return tables


@app.lambda_function()
def database_create(event, context):
    app.log.debug(os.environ['CSW_HOST'])
    app.log.debug(event['User'])
    app.log.debug(event['Database'])

    try:

        app.log.debug("Attempt database connection")

        con = psycopg2.connect(
            database='postgres',
            user=event['User'],
            host=os.environ['CSW_HOST'],
            password=event['Password']
        )

        app.log.debug("Set autocommit to on")
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        # con.autocommit = True

        app.log.debug("Get cursor")
        cur = con.cursor()

        app.log.debug("Execute database create")
        database = event['Database']
        statement = f"CREATE DATABASE {database};"
        status = cur.execute(statement)

        app.log.debug("Close connection")
        cur.close()
        con.close()

    except Exception as err:
        app.log.error(str(err))
        status = False

    return status
