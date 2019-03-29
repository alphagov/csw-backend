"""
AUDIT LAMBDAS
"""
import json
from datetime import datetime
from peewee import Case, fn

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
            audit.save()
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
            CheckClass = app.utilities.get_class_by_name(criterion.invoke_class_name)
            check = CheckClass(app)
            account_id = audit.account_subscription_id.account_id
            check.set_account_subscription_id(audit.account_subscription_id.id)
            session = check.get_session(account=account_id, role=f"{app.prefix}_CstSecurityInspectorRole")

            # check passed is set to true and and-equalsed for all
            # or false and or-equalsed for any
            check_passed = (check.aggregation_type == "all")

            # Mark audit_criterion record as attempted regardless of successful processing
            # This means that we can tell when an audit is finished even if it did not complete
            # Finished = every check was attempted
            # Complete = every check was successfully processed (pass or fail)
            audit_criterion.attempted = True

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

                # check passed is set to true and and-equalsed for all
                # or false and or-equalsed for any
                check_passed = (check.aggregation_type == "all")
                is_all = (check_passed)
                for params in requests:
                    try:
                        data = check.get_data(session, **params)
                        # Set status to true only if data is returned successfully
                        # AccessDenied remains unprocessed
                        status = True
                    except ClientError as boto3_error:
                        # catch access denied type errors from out-of-date policies
                        app.log.error(str(boto3_error))
                        data = None
                    if data is not None:
                        app.log.debug("api response: " + app.utilities.to_json(data))
                        evaluated = []
                        for api_response_item in data:
                            compliance = check.evaluate({}, api_response_item)
                            app.log.debug(app.utilities.to_json(compliance))

                            item_passed = (compliance['status_id'] == 2)

                            # for "any" type checks only passed resources need to be recorded
                            # individual failed resources are irrelevant for any checks.
                            if (is_all or item_passed):

                                audit_resource_item = check.build_audit_resource_item(
                                    api_item = api_response_item,
                                    audit = audit,
                                    criterion = criterion,
                                    params = params
                                )

                                # only check exception status for failed resources
                                if not item_passed:
                                    # insert exception handling here so we catch failed exceptions before they
                                    # change the status of the check
                                    # potentially change the item_passed status before updating check_passed
                                    exception = models.ResourceException.has_active_exception(
                                        criterion.id,
                                        audit_resource_item['resource_persistent_id'],
                                        audit.account_subscription_id.id)

                                    if exception is not None:
                                        item_passed = True
                                        compliance['status_id'] = 4
                                        compliance['is_compliant'] = True
                                        compliance['compliance_type'] = "COMPLIANT"
                                        compliance['annotation'] += f"<p>[Passed by exception: {exception.reason}]</p>"

                                # create an audit_resource record
                                audit_resource = models.AuditResource.create(**audit_resource_item)

                                # populate foreign key for compliance record
                                compliance["audit_resource_id"] = audit_resource
                                audit_resource_item["resource_compliance"] = compliance

                                resource_compliance = models.ResourceCompliance.create(**compliance)  # TODO: unecessary assignment?
                                evaluated.append(audit_resource_item)

                            # update check passed status
                            check_passed = (check_passed and item_passed) if is_all else (check_passed or item_passed)

                        summary = check.summarize(evaluated, summary)
                        app.log.debug(app.utilities.to_json(summary))
                        audit_criterion.resources = summary['all']['display_stat']
                        audit_criterion.tested = summary['applicable']['display_stat']
                        audit_criterion.passed = summary['compliant']['display_stat']
                        audit_criterion.failed = summary['non_compliant']['display_stat']
                        audit_criterion.ignored = summary['not_applicable']['display_stat']
                        audit_criterion.regions = summary['regions']['count']
                        audit_criterion.processed = status
                        # Only update the processed stat if the assume was successful

            # Set the attempted status even if the criterion was not processed
            audit_criterion.save()

            message_data = audit_criterion.serialize()
            message_data['processed'] = status
            message_data['check_passed'] = check_passed
            # It may be worth adding a field to the model
            # to record where a check failed because of a failed assume role
            # message_data['assume_failed'] = (session is None)
            message_body = app.utilities.to_json(message_data)
            message_id = sqs.send_message(
                queue_url,
                message_body
            )  # TODO: unecessary assignment?


    except Exception as err:
        #app.log.error(str(err))
        app.log.error(app.utilities.get_typed_exception(err))
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

            # Processed = count where processed = True
            processed_case = Case(None, [(models.AuditCriterion.processed, 1)], 0)

            # Attempted = count where attempted = True
            attempted_case = Case(None, [(models.AuditCriterion.attempted, 1)], 0)

            # Count where failed resources > 0
            failed_case = Case(None, [(models.AuditCriterion.failed > 0, 1)], 0)

            # Collate stats from audit criteria records
            stats = (models.AuditCriterion.select(
                    fn.COUNT(models.AuditCriterion.id).alias('active_criteria'),
                    fn.SUM(attempted_case).alias('attempted_criteria'),
                    fn.SUM(processed_case).alias('processed_criteria'),
                    fn.SUM(failed_case).alias('failed_criteria'),
                    fn.SUM(models.AuditCriterion.failed).alias('failed_resources')
                )
                .where(models.AuditCriterion.account_audit_id == audit)
                .get())

            app.log.debug((f"Processed: {stats.processed_criteria} "
                           f"Failed checks: {stats.failed_criteria} "
                           f"Failed resources: {stats.failed_resources}"))

            audit.criteria_processed = stats.processed_criteria
            audit.criteria_passed = (stats.processed_criteria - stats.failed_criteria)
            audit.criteria_failed = stats.failed_criteria
            audit.issues_found = stats.failed_resources
            audit.finished = stats.active_criteria == stats.attempted_criteria

            if audit.finished:
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
