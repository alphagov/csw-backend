from chalicelib.models import DatabaseHandle

# native lambda admin function to be invoked
# TODO add authentication or rely on API permissions and assume roles to control access
def database_create_tables(app, event, context):

    try:
        dbh = DatabaseHandle(app)

        table_list = []
        message = ""

        for table_name in event['Tables']:
            model = dbh.get_model(table_name)
            table_list.append(model)

        created = dbh.create_tables(table_list)
    except Exception as err:
        created = False
        message = str(err)

    if created:
        response = ", ".join(event['Tables'])
    else:
        response = f"Table create failed: {message}"
    return response


# def database_create_all_tables(event, context):
    #
    #     try:
    #     dbh = DatabaseHandle(app)
    #
    #   models = dbh.get_models()
    #   table_names = []
    #   table_list = []
    #
    #   for table_name in models:
    #       table_list.append(models[table_name])
    #       table_names.append(table_name)
    #   message = ""
    #
    #   created = dbh.create_tables(table_list)
    # except Exception as err:
    #   created = False
    #   message = str(err)
    #
    # if created:
    #   response = ", ".join(table_names)
    # else:
    #   response = f"Tables created"
    # return response


def database_create_item(app, event, context):

    try:
        dbh = DatabaseHandle(app)

        item = dbh.create_item(event)
        data = item.serialize()
        json_data = app.utilities.to_json(data)

    except Exception:
        json_data = None

    return json_data


def database_get_item(app, event, context):

    app.log.debug('database_get_item function')
    try:

        dbh = DatabaseHandle(app)

        item = dbh.get_item(event)
        data = item.serialize()
        json_data = app.utilities.to_json(data)

    except Exception:
        json_data = None

    return json_data


def database_run(app, event, context):

    try:

        dbh = DatabaseHandle(app)

        dbh.set_credentials(event['User'], event['Password'])
        status = dbh.execute_commands(event['Commands'])
    except Exception:
        status = False

    return status


def database_list_models(app, event, context):

    try:

        dbh = DatabaseHandle(app)

        models = dbh.get_models()
        tables = models.keys()

    except Exception:
        tables = []

    return tables