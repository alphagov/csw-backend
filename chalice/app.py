import logging
import os
import json
from chalice import Chalice, Response, BadRequestError, Rate
from chalicelib.utilities import Utilities
from chalicelib.auth import AuthHandler
from chalicelib.template_handler import TemplateHandler
from chalicelib import audit
from chalicelib import admin
from chalicelib import demos
from chalicelib import route


app = Chalice(app_name='cloud-security-watch')

# switch debug logging on
app.log.setLevel(logging.DEBUG)
app.prefix = os.environ["CSW_ENV"]
app.utilities = Utilities()


def load_route_services():

    app.log.debug('Loading route services')

    try:
        app.auth = AuthHandler(app)

        app.log.debug("Loaded auth")

        app.templates = TemplateHandler(app)

        app.log.debug("Loaded templates")

        app.api.binary_types = [
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

    except Exception as err:
        app.log.error(str(err))


@app.route('/')
def index():

    load_route_services()

    response = app.templates.render_authorized_route_template('/', app.current_request)

    return Response(**response)


@app.route('/logout')
def logout():

    load_route_services()

    response = app.templates.render_authorized_route_template('/logout', app.current_request)

    return Response(**response)


@app.route('/team')
def team_list():
    load_route_services()

    response = route.route_team_list(app)

    return Response(**response)


@app.route('/team/{id}/dashboard')
def team_dashboard(id):
    load_route_services()

    response = route.route_team_dashboard(app, int(id))

    return Response(**response)


@app.route('/audit')
def audit_list():

    load_route_services()

    response = app.templates.render_authorized_route_template('/audit', app.current_request)

    return Response(**response)


@app.route('/audit/{id}')
def audit_report(id):
    load_route_services()
    response = app.templates.render_authorized_route_template('/audit/{id}', app.current_request)

    return Response(**response)


# demo routes with static data
@app.route('/demo')
def demo_index():
    # demo audit data
    app.dummy_data = demos.audit

    load_route_services()
    response = app.templates.render_authorized_route_template(
        '/',
        app.current_request,
        {
            "name": "[User Name]"
        }
    )

    return Response(**response)


@app.route('/demo/audit')
def demo_audit_list():
    # demo audit data
    app.dummy_data = demos.audit

    load_route_services()
    response = app.templates.render_authorized_route_template(
        '/audit',
        app.current_request,
        app.dummy_data
    )

    return Response(**response)


@app.route('/demo/audit/{id}')
def demo_audit_report(id):
    # demo audit data
    app.dummy_data = demos.audit

    load_route_services()
    app.templates = TemplateHandler(app)
    response = app.templates.render_authorized_route_template(
        '/audit/{id}',
        app.current_request,
        app.dummy_data["audits"][0]
    )

    return Response(**response)


# DATABASE ADMIN HELPER LAMBDAS
# native lambda admin function to be invoked
# TODO add authentication or rely on API permissions and assume roles to control access
@app.lambda_function()
def database_create_tables(event, context):
    return admin.execute_database_create_tables(app, event, context)


# @app.lambda_function()
# def database_create_all_tables(event, context):
#   admin.execute_database_create_all_tables(app, event, context)


@app.lambda_function()
def database_create_item(event, context):
    return admin.execute_database_create_item(app, event, context)


@app.lambda_function()
def database_get_item(event, context):
    return admin.execute_database_get_item(app, event, context)


@app.lambda_function()
def database_run(event, context):
    return admin.execute_database_run(app, event, context)


@app.lambda_function()
def database_list_models(event, context):
    return admin.execute_database_list_models(app, event, context)


# AUDIT LAMBDAS START HERE
# @app.schedule(Rate(24, unit=Rate.HOURS))
# def audit_account_schedule(event):
#    return audit.execute_on_audit_accounts_event(app, event, {})


@app.lambda_function()
def audit_account(event, context):
    return audit.execute_on_audit_accounts_event(app, event, context)


@app.on_sqs_message(queue=f"{app.prefix}-audit-account-queue")
def account_audit_criteria(event):
    return audit.execute_on_account_audit_criteria_event(app, event)


@app.on_sqs_message(queue=f"{app.prefix}-audit-account-metric-queue")
def account_evaluate_criteria(event):
    return audit.execute_on_account_evaluate_criteria_event(app, event)


@app.on_sqs_message(queue=f"{app.prefix}-evaluated-metric-queue")
def audit_evaluated_metric(event):
    return audit.execute_on_audit_evaluated_metric_event(app, event)


# TEST ROUTES START HERE - RUN AWS API ON DEMAND
@app.route('/test/ports_ingress_ssh')
def test_ports_ingress_ssh():
    # demo audit data
    app.dummy_data = demos.audit

    response = demos.execute_test_ports_ingress_ssh(app, load_route_services)
    return Response(**response)


@app.route('/test/ports_ingress_open')
def test_ports_ingress_open():
    # demo audit data
    app.dummy_data = demos.audit

    response = demos.execute_test_ports_ingress_open(app, load_route_services)
    return Response(**response)


# ASSET RENDERERS
# TODO This doesn't work for binary file types
@app.route('/assets')
def asset_render_qs():
    load_route_services()
    app.log.debug('asset_render function called by /assets?proxy route')
    try:
        req = app.current_request

        app.log.debug(str(req.uri_params))

        app.log.debug(json.dumps(app.current_request))

        if 'proxy' in req.uri_params:
            proxy = req.uri_params['proxy']

        mime_type = app.utilities.get_mime_type(proxy)

        data = read_asset(proxy)

        return Response(
            body=data,
            status_code=200,
            headers={"Content-Type": mime_type}
        )

    except Exception as e:
        app.log.debug(str(e))
        raise BadRequestError(str(e))


@app.route('/assets/{proxy+}')
def asset_render():
    load_route_services()
    app.log.debug('asset_render function called by /assets/{proxy+} route')
    try:
        req = app.current_request

        app.log.debug(str(req.uri_params))

        if 'proxy' in req.uri_params:
            proxy = req.uri_params['proxy']
        else:
            proxy = req.uri_params['proxy+']

        mime_type = app.utilities.get_mime_type(proxy)

        data = read_asset(proxy)

        return Response(
            body=data,
            status_code=200,
            headers={"Content-Type": mime_type}
        )
    except Exception as e:
        app.log.debug(str(e))
        raise BadRequestError(str(e))


def read_asset(proxy):

    binary_types = app.api.binary_types

    ascii_types = [
        "text/plain",
        "text/css",
        "text/javascript"
    ]

    true_path = os.path.join(os.path.dirname(__file__), 'chalicelib', 'assets', proxy)
    app.log.debug(true_path)

    if ".." in proxy:
        raise Exception(f"No back (..) navigating: {proxy}")

    mime_type = app.utilities.get_mime_type(true_path)

    if mime_type in ascii_types:
        with open(true_path, 'r') as text:
            data = text.read()
    elif mime_type in binary_types:
        with open(true_path, 'rb') as img:
            data = img.read()
    else:
        raise Exception(f"Unsupported file type: {mime_type}")

    return data
