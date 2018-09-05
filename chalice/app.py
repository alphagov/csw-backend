from chalice import Chalice
from chalicelib.models import DatabaseHandle
from chalicelib.aws.gds_sqs_client import GdsSqsClient


app = Chalice(app_name='cloud-security-watch')


@app.route('/')
def index():
    return {'hello': 'world'}


# native lambda admin function to be invoked
# TODO add authentication or rely on API permissions and assume roles to control access
@app.lambda_function()
def database_create_tables(event, context):

    dbh = DatabaseHandle()

    try:
        table_list = []
        message = ""

        # created = True
        for table_name in event['Tables']:
            model = dbh.get_model(table_name)
            table_list.append(model)
            # model.create_table(safe=True)

        created = dbh.create_tables(table_list)
    except Exception as err:
        created = False
        message = str(err)

    if created:
        response = ", ".join(event['Tables'])
    else:
        response = f"Table create failed: {message}"
    return response


@app.lambda_function()
def database_create_item(event, context):

    dbh = DatabaseHandle()

    try:
        item = dbh.create_item(event)
        data = item.serialize()
    except Exception:
        data = None

    return data


@app.lambda_function()
def database_get_item(event, context):

    dbh = DatabaseHandle()

    try:
        item = dbh.get_item(event)
        data = item.serialize()
    except Exception:
        data = None

    return data


@app.lambda_function()
def database_run(event, context):

    dbh = DatabaseHandle()

    try:
        dbh.set_credentials(event['User'], event['Password'])
        status = dbh.execute_commands(event['Commands'])
    except Exception:
        status = False

    return status

@app.lambda_function()
def audit_account(event, context):

    status = False
    dbh = DatabaseHandle()

    try:
        AccountSubscription = dbh.get_model("AccountSubscription")
        AccountAudit = dbh.get_model("AccountAudit")
        active_accounts = AccountSubscription.select().where(AccountSubscription.active == True)
        #.order_by(User.username)

        for account in active_accounts:
            # print(tweet.user.username, '->', tweet.content)

            # create a new empty account audit record
            AccountAudit.create(
                account_subscription_id = account.AccountSubscription
            )

            # create SQS message
            sqs = GdsSqsClient()
            sqs.get_default_client('SQS')

        status = True
    except Exception as err:
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
