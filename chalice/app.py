import magic
import os
# from urllib.parse import urlparse, parse_qs

from chalice import Chalice, Response, BadRequestError

from chalicelib.models import DatabaseHandle
# from chalicelib.auth import AuthHandler
from chalicelib.views import TemplateHandler


app = Chalice(app_name='cloud-security-watch')
# app.auth_handler = AuthHandler()


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


@app.route('/')
def index():

    templates = TemplateHandler()
    request = app.current_request
    response = templates.render_authorized_route_template('/', request)

    return Response(**response)


@app.route('/assets/{proxy+}')
def asset_render():
    try:
        req = app.current_request
        proxy = req.uri_params['proxy']

        binary_types = [
            'application/octet-stream',
            'image/webp',
            'image/apng',
            'image/png',
            'image/svg',
            'image/jpeg',
            'image/x-icon',
            'image/vnd.microsoft.icon',
            'application/x-font-woff',
            'font/woff',
            'font/woff2',
            'font/eot'
        ]

        ascii_types = [
            'text/plain',
            'text/css',
            'text/javascript'
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
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file)
    file_name, ext = os.path.splitext(file)

    if ext == '.js':
        mime_type = 'text/javascript'
    elif ext == '.css':
        mime_type = 'text/css'
    elif ext == '.png':
        mime_type = 'image/png'

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
