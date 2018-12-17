"""
AUDIT LAMBDAS
"""
import json
from datetime import datetime

from botocore.exceptions import ClientError
from chalice import Rate

from app import app
from chalicelib.aws.gds_sqs_client import GdsSqsClient
from chalicelib.aws.gds_ec2_client import GdsEc2Client
from chalicelib import models
from chalicelib.criteria.aws_ec2_security_group_ingress_open import AwsEc2SecurityGroupIngressOpen
from chalicelib.criteria.aws_ec2_security_group_ingress_ssh import AwsEc2SecurityGroupIngressSsh
from chalicelib.criteria.aws_iam_validate_inspector_policy import AwsIamValidateInspectorPolicy
from chalicelib.criteria.aws_support_root_mfa import AwsSupportRootMfa


def get_audit_criteria(app):
    criteria = [
        AwsIamValidateInspectorPolicy,
        AwsEc2SecurityGroupIngressOpen,
        AwsEc2SecurityGroupIngressSsh,
        AwsSupportRootMfa
    ]
    active_criteria = []
    for CriteriaClass in criteria:
        if CriteriaClass.active:
            criteria = CriteriaClass(app)
            active_criteria.append(criteria.describe())
    return active_criteria


def execute_on_audit_accounts_event(event, context):
    try:
        status = False
        active_accounts = models.AccountSubscription.select().where(models.AccountSubscription.active == True)
        app.log.debug("Found active accounts: " + str(len(list(active_accounts))))
        items = []
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
            audit = models.AccountAudit.create(
                account_subscription_id=account
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
    except Exception as err:
        app.log.error("Failed to start audit: " + str(err))
        status = False
        items = []
    return status


@app.schedule(Rate(24, unit=Rate.HOURS))
def audit_account_schedule(event):
    return execute_on_audit_accounts_event(event, {})


@app.lambda_function()
def audit_account(event, context):
    return execute_on_audit_accounts_event(event, context)


@app.on_sqs_message(queue=f"{app.prefix}-audit-account-queue")
def account_audit_criteria(event):
    status = False
    try:
        sqs = GdsSqsClient(app)
        app.log.debug("Invoke SQS client")
        app.log.debug("Set prefix: " + app.prefix)
        queue_url = sqs.get_queue_url(f"{app.prefix}-audit-account-metric-queue")
        app.log.debug("Retrieved queue url: " + queue_url)
        active_criteria = models.Criterion.select().where(models.Criterion.active == True)
        messages = []
        for message in event:
            audit_data = json.loads(message.body)
            app.log.debug(message.body)
            audit = models.AccountAudit.get_by_id(audit_data['id'])
            audit.active_criteria = len(list(active_criteria))
            for criterion in active_criteria:
                audit_criterion = models.AuditCriterion.create(
                    account_audit_id=audit,
                    criterion_id=criterion
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
    return status


# TODO break down into multiple steps
@app.on_sqs_message(queue=f"{app.prefix}-audit-account-metric-queue")
def account_evaluate_criteria(event):
    status = False
    try:
        status = False
        sqs = GdsSqsClient(app)
        app.log.debug("Invoke SQS client")
        app.log.debug("Set prefix: " + app.prefix)
        queue_url = sqs.get_queue_url(f"{app.prefix}-evaluated-metric-queue")
        app.log.debug("Retrieved queue url: " + queue_url)
        for message in event:
            app.log.debug("parse message body")
            audit_criteria_data = json.loads(message.body)
            audit_criterion = models.AuditCriterion.get_by_id(audit_criteria_data["id"])
            app.log.debug("loaded audit criterion")
            audit_data = audit_criteria_data['account_audit_id']
            audit = models.AccountAudit.get_by_id(audit_data['id'])
            app.log.debug("loaded audit")
            criterion_data = audit_criteria_data['criterion_id']
            criterion = models.Criterion.get_by_id(criterion_data['id'])
            app.log.debug("criterion: " + criterion.title)
            provider = criterion_data["criteria_provider_id"]
            app.log.debug("provider: " + provider["provider_name"])
            ClientClass = app.utilities.get_class_by_name(criterion.invoke_class_name)
            client = ClientClass(app)
            account_id = audit.account_subscription_id.account_id
            session = client.get_session(account=account_id, role=f"{app.prefix}_CstSecurityInspectorRole")
            if session is not None:
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
                        data = client.get_data(session, **params)
                    except ClientError as boto3_error:
                        app.log.error(str(boto3_error))
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
                            item_standard = client.translate(item_raw)
                            item.update(item_standard)
                            item_raw.update(item_standard)
                            if "region" in params:
                                item["region"] = params["region"]
                                item_raw["region"] = params["region"]
                            app.log.debug(app.utilities.to_json(item))
                            audit_resource = models.AuditResource.create(**item)
                            compliance["audit_resource_id"] = audit_resource
                            item_raw["resource_compliance"] = compliance
                            resource_compliance = models.ResourceCompliance.create(**compliance)  # TODO: unecessary assignment?
                        summary = client.summarize(data, summary)
                app.log.debug(app.utilities.to_json(summary))
                audit_criterion.resources = summary['all']['display_stat']
                audit_criterion.tested = summary['applicable']['display_stat']
                audit_criterion.passed = summary['compliant']['display_stat']
                audit_criterion.failed = summary['non_compliant']['display_stat']
                audit_criterion.ignored = summary['not_applicable']['display_stat']
                audit_criterion.regions = summary['regions']['count']
                # Only update the processed stat if the assume was successful
                audit.criteria_processed += 1
                audit_criterion.save()

            audit.date_updated = datetime.now()
            message_data = audit_criterion.serialize()
            # It may be worth adding a field to the model
            # to record where a check failed because of a failed assume role
            # message_data['assume_failed'] = (session is None)
            message_body = app.utilities.to_json(message_data)
            message_id = sqs.send_message(
                queue_url,
                message_body
            )  # TODO: unecessary assignment?
            status = True
    except Exception as err:
        app.log.error(str(err))
    return status


@app.on_sqs_message(queue=f"{app.prefix}-evaluated-metric-queue")
def audit_evaluated_metric(event):
    status = False
    try:
        status = False
        sqs = GdsSqsClient(app)
        for message in event:
            audit_criteria_data = json.loads(message.body)
            audit = models.AccountAudit.get_by_id(audit_criteria_data["account_audit_id"]["id"])
            if (audit_criteria_data['failed'] > 0):
                audit.criteria_failed += 1
                audit.issues_found += audit_criteria_data['failed']
            else:
                audit.criteria_passed += 1
            if audit.criteria_processed == audit.active_criteria:
                audit.date_completed = datetime.now()
                message_data = audit.serialize()
                audit_criteria = models.AuditCriterion.select().join(models.AccountAudit).where(
                    models.AccountAudit.id == audit.id
                )
                criteria_data = []
                for criteria in audit_criteria:
                    criteria_data.append(criteria.serialize())
                message_data["criteria"] = criteria_data
                failed_resources = models.ResourceCompliance.select().join(
                    models.AuditResource
                ).join(models.AccountAudit).where(
                    models.ResourceCompliance.status_id == 3, models.AccountAudit.id == audit.id
                )
                resources_data = []
                for resource in failed_resources:
                    resources_data.append(resource.serialize())
                message_data["failed_resources"] = resources_data
                # create SQS message
                queue_url = sqs.get_queue_url(f"{app.prefix}-completed-audit-queue")
                app.log.debug("Retrieved queue url: " + queue_url)
                message_body = app.utilities.to_json(message_data)
                try:
                    latest = models.AccountLatestAudit.get(
                        models.AccountLatestAudit.account_subscription_id == audit.account_subscription_id
                    )
                    latest.account_audit_id = audit
                    latest.save()
                except models.AccountLatestAudit.DoesNotExist:
                    latest = models.AccountLatestAudit.create(
                        account_subscription_id=audit.account_subscription_id,
                        account_audit_id=audit
                    )
                app.log.debug("latest_audit: " + app.utilities.to_json(latest.serialize()))
                message_id = sqs.send_message(
                    queue_url,
                    message_body
                )  # TODO: unecessary assignment?
            audit.save()
    except Exception as err:
        app.log.error(str(err))
    return status
