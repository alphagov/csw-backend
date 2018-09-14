import logging
import os
import json
from botocore.exceptions import ClientError
from datetime import datetime
from chalice import Chalice, Response, BadRequestError, Rate
from chalicelib.utilities import Utilities
from chalicelib.auth import AuthHandler
from chalicelib.aws.gds_sqs_client import GdsSqsClient
from chalicelib.aws.gds_ec2_client import GdsEc2Client
from chalicelib.models import DatabaseHandle
from chalicelib.views import TemplateHandler


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

    app.log.debug('Try loading route services')

    load_route_services()

    app.log.debug('Loaded route services')

    response = app.templates.render_authorized_route_template('/', app.current_request)

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
def demo_index():
    load_route_services()
    response = app.templates.render_authorized_route_template('/',
        app.current_request,
        { "name": "[User Name]" }
    )

    return Response(**response)


@app.route('/demo/audit')
def demo_audit_list():
    load_route_services()
    response = app.templates.render_authorized_route_template('/audit',
        app.current_request,
        app.dummy_data
    )

    return Response(**response)


@app.route('/demo/audit/{id}')
def demo_audit_report(id):
    load_route_services()
    app.templates = TemplateHandler(app)
    response = app.templates.render_authorized_route_template('/audit/{id}',
        app.current_request,
        app.dummy_data["audits"][0]
    )

    return Response(**response)



# native lambda admin function to be invoked
# TODO add authentication or rely on API permissions and assume roles to control access
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
        created = False
        message = str(err)

    if created:
        response = ", ".join(event['Tables'])
    else:
        response = f"Table create failed: {message}"
    return response


# @app.lambda_function()
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


@app.lambda_function()
def database_create_item(event, context):

    try:
        dbh = DatabaseHandle(app)

        item = dbh.create_item(event)
        data = item.serialize()
        json_data = app.utilities.to_json(data)

    except Exception:
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

    except Exception:
        json_data = None

    return json_data


@app.lambda_function()
def database_run(event, context):

    try:

        dbh = DatabaseHandle(app)

        dbh.set_credentials(event['User'], event['Password'])
        status = dbh.execute_commands(event['Commands'])
    except Exception:
        status = False

    return status


@app.lambda_function()
def database_list_models(event, context):

    try:

        dbh = DatabaseHandle(app)

        models = dbh.get_models()
        tables = models.keys()

    except Exception:
        tables = []

    return tables

@app.schedule(Rate(24, unit=Rate.HOURS))
def audit_account_schedule(event):
    return Response(**{
        "body": "not yet implemented"
    })

@app.lambda_function()
def audit_account(event, context):
    db = None
    try:
        status = False
        dbh = DatabaseHandle(app)

        db = dbh.get_handle()
        db.connect()

        AccountSubscription = dbh.get_model("AccountSubscription")
        AccountAudit = dbh.get_model("AccountAudit")
        active_accounts = (AccountSubscription.select().where(AccountSubscription.active == True))

        items = []
        # .order_by(User.username)

        # create SQS message
        sqs = GdsSqsClient(app)

        app.log.debug("Invoke SQS client")

        app.log.debug("Set prefix: " + app.prefix)

        queue_url = sqs.get_queue_url(f"{app.prefix}-audit-account-queue")

        app.log.debug("Retrieved queue url: " + queue_url)

        for account in active_accounts:

            app.log.debug("Audit account: " + account.account_name)
            items.append(account.serialize())

            # create a new empty account audit record
            audit = AccountAudit.create(
                account_subscription_id = account
            )

            app.log.debug("Created audit record")

            message_body = app.utilities.to_json(audit.serialize())

            app.log.debug("Sending SQS message with body: " + message_body)

            message_id = sqs.send_message(
                queue_url,
                message_body
            )

            if message_id is not None:
                app.log.debug("Sent SQS message: " + message_id)
            else:
                raise Exception("Message ID empty from SQS send_message")

        status = True
        db.close()

    except Exception as err:

        app.log.error("Failed to start audit: " + str(err))
        status = False
        items = []
        if db is not None:
            db.rollback()
            db.close()

    return status


@app.on_sqs_message(queue=f"{app.prefix}-audit-account-queue")
def account_audit_criteria(event):

    status = False
    try:

        dbh = DatabaseHandle(app)

        db = dbh.get_handle()
        db.connect()

        AccountAudit = dbh.get_model("AccountAudit")
        Criterion = dbh.get_model("Criterion")
        AuditCriterion = dbh.get_model("AuditCriterion")

        # create SQS message
        sqs = GdsSqsClient(app)

        app.log.debug("Invoke SQS client")

        app.log.debug("Set prefix: " + app.prefix)

        queue_url = sqs.get_queue_url(f"{app.prefix}-audit-account-metric-queue")

        app.log.debug("Retrieved queue url: " + queue_url)

        active_criteria = (Criterion.select().where(Criterion.active == True))

        messages = []

        for message in event:

            audit_data = json.loads(message.body)

            app.log.debug(message.body)

            audit = AccountAudit.get_by_id(audit_data['id'])
            audit.active_criteria = len(list(active_criteria))

            for criterion in active_criteria:

                audit_criterion = AuditCriterion.create(
                    account_audit_id = audit,
                    criterion_id = criterion
                )

                message_body = app.utilities.to_json(audit_criterion.serialize())

                message_id = sqs.send_message(
                    queue_url,
                    message_body
                )

                messages.append(message_id)

            audit.date_updated = datetime.now()
            audit.save()

    except Exception as err:
        app.log.error(str(err))
        if db is not None:
            db.rollback()
            db.close()

    return status


@app.on_sqs_message(queue=f"{app.prefix}-audit-account-metric-queue")
def account_evaluate_criteria(event):

    status = False
    try:
        status = False
        dbh = DatabaseHandle(app)

        db = dbh.get_handle()
        db.connect()

        sqs = GdsSqsClient(app)

        Criterion = dbh.get_model("Criterion")
        AccountAudit = dbh.get_model("AccountAudit")
        AuditResource = dbh.get_model("AuditResource")
        AuditCriterion = dbh.get_model("AuditCriterion")
        ResourceCompliance = dbh.get_model("ResourceCompliance")

        # create SQS message
        sqs = GdsSqsClient(app)

        app.log.debug("Invoke SQS client")

        app.log.debug("Set prefix: " + app.prefix)

        queue_url = sqs.get_queue_url(f"{app.prefix}-audit-account-metric-queue")

        app.log.debug("Retrieved queue url: " + queue_url)

        messages = []

        for message in event:
            audit_criteria_data = json.loads(message.body)

            audit_criterion = AuditCriterion.get_by_id(audit_criteria_data["id"])

            audit_data = audit_criteria_data['account_audit_id']

            audit = AccountAudit.get_by_id(audit_data['id'])

            criterion_data = audit_criteria_data['criterion_id']

            criterion = Criterion.get_by_id(criterion_data['id'])

            app.log.debug("criterion: " + criterion.title)

            provider = criterion_data["criteria_provider_id"]

            app.log.debug("provider: " + provider["provider_name"])

            ClientClass = app.utilities.get_class_by_name(criterion.invoke_class_name)
            client = ClientClass(app)

            account_id = audit.account_subscription_id.account_id

            session = client.get_session(account=account_id, role=f"{app.prefix}_CstSecurityInspectorRole")

            method = criterion.invoke_class_get_data_method

            app.log.debug("get data method: " + method)

            params = {}
            for param in criterion.criterion_params:
                params[param.param_name] = param.param_value

            app.log.debug("params: " + app.utilities.to_json(params))

            requests = []
            if criterion.is_regional:
                ec2 = GdsEc2Client(app)
                regions = ec2.describe_regions()
                for region in regions:
                    region_params = params.copy()
                    region_params["region"] = region["RegionName"]
                    app.log.debug("Create request from region: " + region_params["region"])
                    requests.append(region_params)

            else:
                requests.append(params)

            summary = None
            for params in requests:

                try:
                    data = getattr(client, method)(session, **params)
                except ClientError as boto3_error:
                    app.log.error(str(boto3_error))
                    audit.criteria_failed += 1
                    data = None

                if data is not None:

                    app.log.debug("api response: " + app.utilities.to_json(data))

                    for item_raw in data:

                        compliance = client.evaluate({}, item_raw)

                        app.log.debug(app.utilities.to_json(compliance))

                        item = {
                            "account_audit_id": audit.id,
                            "criterion_id": criterion.id,
                            "resource_data": app.utilities.to_json(item_raw),
                            "date_evaluated": datetime.now()
                        }

                        if "region" in params:
                            item["region"] = params["region"]

                        item.update(client.translate(item_raw))

                        app.log.debug(app.utilities.to_json(item))

                        audit_resource = AuditResource.create(**item)

                        compliance["audit_resource_id"] = audit_resource

                        item_raw["resource_compliance"] = compliance

                        resource_compliance = ResourceCompliance.create(**compliance)

                    summary = client.summarize(data, summary)

            app.log.debug(app.utilities.to_json(summary))

            audit_criterion.resources = summary['all']['display_stat']
            audit_criterion.tested = summary['applicable']['display_stat']
            audit_criterion.passed = summary['compliant']['display_stat']
            audit_criterion.failed = summary['non_compliant']['display_stat']
            audit_criterion.ignored = summary['not_applicable']['display_stat']
            audit_criterion.save()

            audit.date_updated = datetime.now()

            queue_url = sqs.get_queue_url(f"{app.prefix}-evaluated-metric-queue")

            app.log.debug("Retrieved queue url: " + queue_url)

            message_body = app.utilities.to_json(audit_criterion.serialize())

            message_id = sqs.send_message(
                queue_url,
                message_body
            )

            status = True

    except Exception as err:
        app.log.error(str(err))
        if db is not None:
            db.rollback()
            db.close()

    return status


@app.on_sqs_message(queue=f"{app.prefix}-evaluated-metric-queue")
def evaluated_metric(event):
    status = False
    try:
        status = False
        dbh = DatabaseHandle(app)

        db = dbh.get_handle()
        db.connect()

        sqs = GdsSqsClient(app)
        AccountAudit = dbh.get_model("AccountAudit")
        AuditCriterion = dbh.get_model("AuditCriterion")
        AuditResource = dbh.get_model("AuditResource")
        ResourceCompliance = dbh.get_model("ResourceCompliance")

        for message in event:
            audit_criteria_data = json.loads(message.body)

            audit = AccountAudit.get_by_id(audit_criteria_data["account_audit_id"]["id"])
            audit.criteria_processed += 1

            if audit.criteria_processed == audit.active_criteria:
                audit.date_completed = datetime.now()

                message_data = audit.serialize()

                audit_criteria = (AuditCriterion.select().join(AccountAudit).where(AccountAudit.id == audit.id))

                criteria_data = []
                for criteria in audit_criteria:
                    criteria_data.append(criteria.serlialize())

                message_data["criteria"] = criteria_data

                failed_resources = (AuditResource.select().join(AccountAudit).join(ResourceCompliance).where(AccountAudit == audit, ResourceCompliance.status == 3))

                resources_data = []
                for resource in failed_resources:
                    resources_data.append(resource.serialize(True))

                message_data["failed_resources"] = resources_data

                # create SQS message
                queue_url = sqs.get_queue_url(f"{app.prefix}-completed-audit-queue")

                app.log.debug("Retrieved queue url: " + queue_url)

                message_body = app.utilities.to_json(message_data)

                message_id = sqs.send_message(
                    queue_url,
                    message_body
                )

            audit.save()

    except Exception as err:
        app.log.error(str(err))
        if db is not None:
            db.rollback()
            db.close()

    return status


@app.route('/test/ports_ingress_ssh')
def test_ports_ingress_ssh():

    try:
        load_route_services()

        Client = app.utilities.get_class_by_name(
            "chalicelib.criteria.aws_ec2_security_group_ingress_ssh.AwsEc2SecurityGroupIngressSsh"
        )
        ec2 = Client(app)

        session = ec2.get_session(account='103495720024', role='csw-dan_CstSecurityInspectorRole')

        groups = ec2.describe_security_groups(session, **{"region": 'eu-west-1'})

        for group in groups:
            compliance = ec2.evaluate({}, group, [])

            app.log.debug(app.utilities.to_json(compliance))

            group['resource_compliance'] = compliance

        summary = ec2.summarize(groups)

        template_data = app.dummy_data["audits"][0]
        template_data["criteria"][0]["compliance_results"] = groups
        template_data["criteria"][0]["compliance_summary"] = summary
        template_data["criteria"][0]["tested"] = True

        response = app.templates.render_authorized_route_template(
            '/audit/{id}',
            app.current_request,
            template_data
        )
    except Exception as err:
        response = { "body": str(err) }

    return Response(**response)


@app.route('/test/ports_ingress_open')
def test_ports_ingress_open():


    try:
        load_route_services()

        Client = app.utilities.get_class_by_name(
            "chalicelib.criteria.aws_ec2_security_group_ingress_open.AwsEc2SecurityGroupIngressOpen"
        )
        ec2 = Client(app)

        session = ec2.get_session(account='103495720024', role='csw-dan_CstSecurityInspectorRole')

        groups = ec2.describe_security_groups(session, **{ "region": 'eu-west-1'})

        for group in groups:

            compliance = ec2.evaluate({}, group, [])

            app.log.debug(app.utilities.to_json(compliance))

            group['resource_compliance'] = compliance

        summary = ec2.summarize(groups)

        template_data = app.dummy_data["audits"][0]
        template_data["criteria"][0]["compliance_results"] = groups
        template_data["criteria"][0]["compliance_summary"] = summary
        template_data["criteria"][0]["tested"] = True

        response = app.templates.render_authorized_route_template(
            '/audit/{id}',
            app.current_request,
            template_data
        )
    except Exception as err:
        response = { "body": str(err) }

    return Response(**response)


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

