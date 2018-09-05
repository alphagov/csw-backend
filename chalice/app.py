import os
# from urllib.parse import urlparse, parse_qs

from chalice import Chalice, Response, BadRequestError

from chalicelib.models import DatabaseHandle
from chalicelib.aws.gds_sqs_client import GdsSqsClient
#from chalicelib.views import TemplateHandler
from chalicelib.auth import AuthHandler


app = Chalice(app_name='cloud-security-watch')
app.auth = AuthHandler()


@app.route('/')
def index():

    response = {
        "body": "Test without auth and templates",
        "headers": {
            "Content-type": "text/html"
        }
    }

    #templates = TemplateHandler(app.auth)
    #request = app.current_request
    #response = templates.render_authorized_route_template('/', request)

    return Response(**response)


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



@app.route('/assets/{proxy+}')
def asset_render():
    try:
        req = app.current_request
        proxy = req.uri_params['proxy']

        binary_types = [
            "application/octet-stream",
            "image/webp",
            "image/apng",
            "image/png",
            "image/svg",
            "image/jpeg",
            "image/x-icon",
            "image/vnd.microsoft.icon",
            "application/x-font-woff",
            "font/woff",
            "font/woff2",
            "font/eot"
        ]

        ascii_types = [
            "text/plain",
            "text/css",
            "text/javascript"
        ]

        true_path = os.path.join(os.path.dirname(__file__), 'chalicelib', 'templates', proxy)

        if ".." in proxy:
            raise Exception(f"No back (..) navigating: {proxy}")

        mime_type = get_mime_type(true_path)

        if mime_type in ascii_types:
            with open(true_path, 'r') as text:
                data = text.read()
        elif mime_type in binary_types:
            with open(true_path, 'rb') as img:
                data = img.read()
        else:
            raise Exception(f"Unsupported file type: {mime_type}")

        return Response(
            body=data,
            status_code=200,
            headers={"Content-Type": mime_type}
        )
    except Exception as e:
        raise BadRequestError(str(e))


def get_mime_type(file):
    # I've removed the python-magic library because the
    # it fails to be installed in the chalice deploy
    # and returns the wrong type for a number of common types
    file_name, ext = os.path.splitext(file)

    known_types = {
        ".html": "text/html",
        ".js": "text/javascript",
        ".css": "text/css",
        ".svg": "image/svg",
        ".png": "image/png",
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg",
        ".ico": "image/x-icon",
        ".woff": "font/woff",
        ".woff2": "font/woff",
        ".eot": "font/eot",
        ".txt": "text/plain",
        ".md": "text/plain"
    }

    default_type = "application/octet-stream"

    if ext in known_types:
        mime_type = known_types[ext]
    else:
        mime_type = default_type

    return mime_type


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
