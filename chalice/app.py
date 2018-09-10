import logging
import os
import json
from datetime import datetime
from chalice import Chalice, Response, BadRequestError
from chalicelib.auth import AuthHandler
from chalicelib.aws.gds_sqs_client import GdsSqsClient
from chalicelib.aws.gds_ec2_client import GdsEc2Client
from chalicelib.models import DatabaseHandle
from chalicelib.views import TemplateHandler

from chalicelib.evaluators.evaluator_ports_ingress_ssh import EvaluatorPortsIngressSsh


app = Chalice(app_name='cloud-security-watch')

# switch debug logging on
app.log.setLevel(logging.DEBUG)
print(app.log.getEffectiveLevel())

app.auth = AuthHandler(app)
app.templates = TemplateHandler(app)
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


@app.route('/')
def index():

    response = app.templates.render_authorized_route_template('/', app.current_request)

    return Response(**response)


@app.route('/audit')
def audit_list():

    response = app.templates.render_authorized_route_template('/audit', app.current_request)

    return Response(**response)


@app.route('/audit/{id}')
def audit_report(id):

    response = app.templates.render_authorized_route_template('/audit/{id}', app.current_request)

    return Response(**response)


# demo audit data
app.dummy_data = {
    "name": "[User Name]",
    "audits": [
        {
            "name": "[User Name]",
            "id": 1,
            "account_subscription": {
                "account_id": 779799343306,
                "account_name": "gds-digital-security"
            },
            "date_started": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "date_updated": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "date_completed": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "active_criteria": 5,
            "criteria_processed": 5,
            "criteria_analysed": 2,
            "criteria_failed": 3,
            "issues_found": 2,
            "criteria": [
                {
                    "id": 1,
                    "name": "SSH port ingress too open",
                    "tested": False,
                    "why_is_it_important": "Opening ports to the world exposes a greater risk if an SSH key is leaked",
                    "how_do_i_fix_it": "The SSH port (22) should only be open to known GDS IP addresses including the cabinet office VPN",
                    "processed": "yes",
                    "status": "fail",
                    "issues": 1,
                    "resources": [
                        {
                            "arn": "arn-1",
                            "status": "pass",
                            "issues": "",
                            "advice": ""
                        },
                        {
                            "arn": "arn-2",
                            "status": "fail",
                            "issues": "",
                            "advice": ""
                        }
                    ]
                },
                {
                    "id": 2,
                    "name": "Security groups with open egress",
                    "tested": False,
                    "why_is_it_important": "Opening ports to the world exposes a greater risk of data been sent out from the service to an unknown location",
                    "how_do_i_fix_it": "The egress rules should specify which ports can be used. Only http(s) should be open to the world and through a proxy service so that we can record traffic.",
                    "processed": "yes",
                    "status": "fail",
                    "issues": 1,
                    "resources": [
                        {
                            "arn": "arn-1",
                            "status": "pass",
                            "issues": "",
                            "advice": ""
                        },
                        {
                            "arn": "arn-2",
                            "status": "fail",
                            "issues": "The security group can connect outbound to anywhere",
                            "advice": "You can remediate this by narrowing the ports or ip ranges."
                        }
                    ]
                }
            ]
        }
    ]
}


# demo routes with static data
@app.route('/demo')
def index():

    response = app.templates.render_authorized_route_template('/',
        app.current_request,
        { "name": "[User Name]" }
    )

    return Response(**response)


@app.route('/demo/audit')
def audit_list():

    response = app.templates.render_authorized_route_template('/audit',
        app.current_request,
        app.dummy_data
    )

    return Response(**response)


@app.route('/demo/audit/{id}')
def audit_report(id):

    response = app.templates.render_authorized_route_template('/audit/{id}',
        app.current_request,
        app.dummy_data["audits"][0]
    )

    return Response(**response)

# native lambda admin function to be invoked
# TODO add authentication or rely on API permissions and assume roles to control access
@app.lambda_function()
def database_create_tables(event, context):

    dbh = DatabaseHandle()

    try:
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


@app.lambda_function()
def database_create_all_tables(event, context):
    dbh = DatabaseHandle()

    try:
        table_list = dbh.get_models()
        message = ""

        created = dbh.create_tables(table_list)
    except Exception as err:
        created = False
        message = str(err)

    if created:
        response = ", ".join(event['Tables'])
    else:
        response = f"Tables created"
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
        # .order_by(User.username)

        for account in active_accounts:

            # create a new empty account audit record
            audit = AccountAudit.create(
                account_subscription_id = account.AccountSubscription
            )

            # create SQS message
            sqs = GdsSqsClient()
            sqs_client = sqs.get_default_client('sqs')
            prefix = os.environ["CSW_ENV"]

            queue_url = sqs_client.get_queue_url(f"{prefix}-audit-account-queue.fifo")
            message_body = json.dumps(audit)

            message_id = sqs_client.send_message(
                queue_url,
                message_body
            )

        status = True
    except Exception as err:
        status = False

    return status


@app.route('/test/ports_ingress_ssh')
def test_assume():

    try:
        ec2 = GdsEc2Client(app)
        session = ec2.get_session(account='103495720024', role='sandbox_cst_security_inspector_role')

        app.log.debug("session: " + str(session))

        groups = ec2.describe_security_groups(session, region='eu-west-1')

        app.log.debug("groups: " + str(groups))

        evaluator = EvaluatorPortsIngressSsh(app)

        summary = {
            'all': {
                'display_stat': 0,
                'category': 'all',
                'modifier_class': 'tested'
            },
            'applicable': {
                'display_stat': 0,
                'category': 'tested',
                'modifier_class': 'precheck'
            },
            'non_compliant': {
                'display_stat': 0,
                'category': 'failed',
                'modifier_class': 'failed'
            },
            'compliant': {
                'display_stat': 0,
                'category': 'passed',
                'modifier_class': 'passed'
            },
            'non_applicable': {
                'display_stat': 0,
                'category': 'ignored',
                'modifier_class': 'passed'
            }
        }

        for group in groups:

            group['resourceType'] = 'AWS::EC2::SecurityGroup'

            app.log.debug('set resource type')

            compliance = evaluator.evaluate_compliance({}, group, [])

            summary['all']['display_stat'] += 1

            if compliance['IsApplicable']:
                summary['applicable']['display_stat'] += 1

                if compliance['IsCompliant']:
                    summary['compliant']['display_stat'] += 1
                else:
                    summary['non_compliant']['display_stat'] += 1

            else:
                summary['non_applicable']['display_stat'] += 1

            group['compliance'] = compliance

            app.log.debug(str(compliance))

        template_data = app.dummy_data["audits"][0]

        template_data["criteria"][0]["compliance_results"] = groups
        template_data["criteria"][0]["compliance_summary"] = summary
        template_data["criteria"][0]["tested"] = True

        app.log.debug("template data: " + str(template_data))

        response = app.templates.render_authorized_route_template('/audit/{id}',
            app.current_request,
            template_data
        )
    except Exception as err:
        { "body": str(err) }

    return Response(**response)



@app.route('/assets/{proxy+}')
def asset_render():

    app.log.debug('asset_render function called by /assets/{proxy+} route')
    try:
        req = app.current_request

        app.log.debug(str(req.uri_params))

        if 'proxy' in req.uri_params:
            proxy = req.uri_params['proxy']
        else:
            proxy = req.uri_params['proxy+']

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
        print(str(e))
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
