"""
DATABASE ADMIN HELPER LAMBDAS
native lambda admin function to be invoked
"""
# TODO add authentication or rely on API permissions and assume roles to control access
import importlib
import inspect
import os
import pkgutil
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from app import app, load_route_services
from chalicelib.database_handle import DatabaseHandle
from chalicelib import models


@app.lambda_function()
def database_create(event, context):
    app.log.debug(os.environ["CSW_HOST"])
    app.log.debug(event["User"])
    app.log.debug(event["Database"])

    try:

        app.log.debug("Attempt database connection")

        con = psycopg2.connect(
            database="postgres",
            user=event["User"],
            host=os.environ["CSW_HOST"],
            password=event["Password"],
        )

        app.log.debug("Set autocommit to on")
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        # con.autocommit = True

        app.log.debug("Get cursor")
        cur = con.cursor()

        app.log.debug("Execute database create")
        database = event["Database"]
        statement = f"CREATE DATABASE {database};"
        status = cur.execute(statement)

        app.log.debug("Close connection")
        cur.close()
        con.close()

    except Exception as err:
        app.log.error(str(err))
        status = False

    return status


@app.lambda_function()
def database_create_tables(event, context):
    try:
        dbh = DatabaseHandle(app)
        table_list = []
        message = ""
        for table_name in event["Tables"]:
            model = dbh.get_model(table_name)
            table_list.append(model)
        created = dbh.create_tables(table_list)
    except Exception as err:
        app.log.error(str(err))
        created = False
        message = str(err)
    if created:
        response = ", ".join(event["Tables"])
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
    app.log.debug("database_get_item function")
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
def database_get_all_items(event, context):
    app.log.debug("database_get_all_items function")
    try:
        data = []
        n = 0
        dbh = DatabaseHandle(app)
        db = dbh.get_handle()
        db.connect()
        model = dbh.get_model(event["Model"])
        for item in model.select():
            serialised_record = item.serialize()
            data.append(serialised_record)
            n += 1
            app.log.debug(str(serialised_record))
        app.log.debug(f"database_get_all_items fetched {n} records")
        db.close()
        json_data = app.utilities.to_json(data)
    except Exception as err:
        app.log.error(str(err))
        json_data = None
    return json_data


@app.lambda_function()
def database_run(event, context):
    try:
        dbh = DatabaseHandle(app)
        dbh.set_credentials(event["User"], event["Password"])
        status = dbh.execute_commands(event["Commands"])
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
    return list(tables)


def criteria_finder(parent_module_name="chalicelib.criteria"):
    """
    A helper function returning a set with all classes in the chalicelib.criteria submodules
    having a class attribute named "active" with value `True`.
    """
    parent_module = importlib.import_module(parent_module_name)
    active_criteria = set()

    for loader, module_name, ispkg in pkgutil.iter_modules(parent_module.__path__):

        parent_module_import_path = f"{parent_module.__name__}.{module_name}"

        members = inspect.getmembers(
            importlib.import_module(parent_module_import_path), inspect.isclass
        )
        for name, cls in members:
            is_criteria_default = "CriteriaDefault" in [
                supercls.__name__ for supercls in inspect.getmro(cls)
            ]
            if is_criteria_default:
                active_criteria.add(f"{parent_module_import_path}.{name}")

    return active_criteria


@app.lambda_function()
def database_add_new_criteria(event, context):
    # try:
    dbh = DatabaseHandle(app)
    for criterion in criteria_finder():
        app.log.debug(f"Updating criterion: {criterion}")
        dbh.create_or_update_criterion({"criterion_name": criterion})
    # except Exception as err:
    #     app.log.error(str(err))
    return None


@app.lambda_function()
def update_teams(event, context):
    teams = models.ProductTeam.select()
    for team in teams:
        team_settings = get_team_settings(team)
    return None