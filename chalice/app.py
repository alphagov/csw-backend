from chalice import Chalice
from chalicelib.models import DatabaseHandle


app = Chalice(app_name='cloud-security-watch')


@app.route('/')
def index():
    return {'hello': 'world'}


# native lambda admin function to be invoked
# TODO add authentication or rely on API permissions and assume roles to control access
@app.lambda_function()
def database_create_tables(event, context):

    db = DatabaseHandle()

    try:
        table_list = []

        # created = True
        for table_name in event['Tables']:
            model = db.get_model(table_name)
            table_list.append(model)
            # model.create_table(safe=True)

        created = db.create_tables(table_list)
    except Exception:
        created = False
        db.rollback()

    if created:
        response = ", ".join(event['Tables'])
    else:
        response = "Table create failed"
    return response


@app.lambda_function()
def database_create_item(event, context):

    db = DatabaseHandle()

    try:
        item = db.create_item(event)
        data = item.serialize()
    except Exception:
        db.rollback()

    return data


@app.lambda_function()
def database_get_item(event, context):

    db = DatabaseHandle()

    try:
        item = db.get_item(event)
        data = item.serialize()
    except Exception:
        db.rollback()

    return data


@app.lambda_function()
def database_run(event, context):

    db = DatabaseHandle()

    try:
        db.set_credentials(event['User'], event['Password'])
        status = db.execute_commands(event['Commands'])
    except Exception:
        status = False

    return status

# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
