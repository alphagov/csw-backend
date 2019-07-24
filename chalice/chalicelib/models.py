import os
import datetime
import peewee
import re

# peewee has a validator library but it has a max version of 3.1
# this would mean downgrading our peewee version.
# essentially it provides some simple validators and then
# allows you to create custom validators with a standard method signature
# seemed better to rewrite than downgrade
# from peewee_validates import ModelValidator

from app import app  # used only for logging
from chalicelib import database_handle
from chalicelib.peewee_models.user import User
from chalicelib.peewee_models.user_session import UserSession
from chalicelib.peewee_models.product_team import ProductTeam
from chalicelib.peewee_models.product_team_user import ProductTeamUser
from chalicelib.peewee_models.account_subscription import AccountSubscription


# When an audit is triggered an audit record is created which
# counts each criteria as it is measured so that we know
# when an audit is complete

# There is a bit of overkill in terms of storing numbers which
# makes it easy to track progress when we're working with lambdas

# active_criteria = the criteria present at the start of the audit
# criteria_processed = we've tried to audit that criterion
# criteria_analysed = we audited it successfully
# criteria_failed = we were unable to get the data or complete the audit

# a completed audit should have
# active_criteria = criteria_processed
# = (criteria_analysed + criteria_failed)

# a successful audit should have
# active_criteria = criteria_analysed
from chalicelib.peewee_models.account_audit import AccountAudit
from chalicelib.peewee_models.account_latest_audit import AccountLatestAudit

# eg AWS domain - Trusted Advisor EC2...
# The tool could be extended beyond the scope of AWS
class CriteriaProvider(database_handle.BaseModel):
    provider_name = peewee.CharField()

    class Meta:
        table_name = "criteria_provider"


# eg Trusted Advisor - Security Groups - Specific Ports Unrestricted
# invoke_class_method like describe_trusted_advisor_check_result
class Criterion(database_handle.BaseModel):
    criterion_name = peewee.CharField()
    # TODO: remove the FK below and its class above, not used
    criteria_provider_id = peewee.ForeignKeyField(CriteriaProvider, backref="criteria")
    invoke_class_name = peewee.CharField()
    invoke_class_get_data_method = peewee.CharField()
    title = peewee.TextField()
    description = peewee.TextField()
    why_is_it_important = peewee.TextField()
    how_do_i_fix_it = peewee.TextField()
    active = peewee.BooleanField(default=True)
    is_regional = peewee.BooleanField(default=True)
    severity = peewee.IntegerField(default=1)

    class Meta:
        table_name = "criterion"


# Primarily for trusted advisor checks specifies arguments that need to be provided
# eg
# language=en
# checkId=HCP4007jGY (for Security Groups - Specific Ports Unrestricted)
class CriterionParams(database_handle.BaseModel):
    criterion_id = peewee.ForeignKeyField(Criterion, backref="criterion_params")
    param_name = peewee.CharField()
    param_value = peewee.CharField()

    class Meta:
        table_name = "criterion_params"


# We may want more statuses than Red/Amber/Green
class Status(database_handle.BaseModel):
    status_name = peewee.CharField()
    description = peewee.TextField()

    class Meta:
        table_name = "status"


# For metrics and accepted risks we can associate a severity which
# allows us to float higher value issues to the top
class Severity(database_handle.BaseModel):
    severity_name = peewee.CharField()
    description = peewee.TextField()

    class Meta:
        table_name = "severity"


# For metrics and accepted risks we can associate a severity which
# allows us to float higher value issues to the top
# notification classes should extend a base Notification class
# and then override a notify method
# This is a stub that will need to be expanded to enable reporting to things like ZenDesk
class NotificationMethod(database_handle.BaseModel):
    system_name = peewee.CharField()
    description = peewee.TextField()
    invoke_class_name = peewee.CharField()

    class Meta:
        table_name = "notification_method"


# For each audit if we're querying the same domain and the same
# method for multiple checks (eg ec2 describe-security-groups)
# we can get the data once, store and re-use it rather than calling
# the api to get the same data multiple times.

# If it's part of a separate audit we need to do it again

# It has a generic name since we may choose to get the AWS data
# via splunk in the future or we could broaden the reach of the
# tool to check other vulnerabilities.
class CachedDataResponse(database_handle.BaseModel):
    criterion_id = peewee.ForeignKeyField(Criterion, backref="cached_data_responses")
    account_audit_id = peewee.ForeignKeyField(
        AccountAudit, backref="cached_data_responses"
    )
    invoke_class_name = peewee.CharField()
    invoke_class_get_data_method = peewee.CharField()
    response = peewee.TextField()

    class Meta:
        table_name = "cached_data_response"


class AuditCriterion(database_handle.BaseModel):
    criterion_id = peewee.ForeignKeyField(Criterion, backref="audit_criteria")
    account_audit_id = peewee.ForeignKeyField(AccountAudit, backref="audit_criteria")
    regions = peewee.IntegerField(default=0)
    resources = peewee.IntegerField(default=0)
    tested = peewee.IntegerField(default=0)
    passed = peewee.IntegerField(default=0)
    failed = peewee.IntegerField(default=0)
    ignored = peewee.IntegerField(default=0)
    processed = peewee.BooleanField(default=False)
    attempted = peewee.BooleanField(default=False)

    class Meta:
        table_name = "audit_criterion"

    def get_resources_by_status(self, status_id):
        account_audit_id = self.account_audit_id

        try:
            criterion = self.criterion_id

            return (
                ResourceCompliance.select()
                .join(AuditResource)
                .where(
                    AuditResource.criterion_id == criterion.id,
                    AuditResource.account_audit_id == account_audit_id,
                    ResourceCompliance.status_id == status_id,
                )
            )
        except Exception as err:
            self.app.log.error("Failed to get audit resources: " + str(err))
            return []

    def get_failed_resources(self):
        # Kept method definition in case it's used elsewhere
        return self.get_resources_by_status(3)

    def get_issues_list(self):
        account_issues = self.get_resources_by_status(3)
        issues_list = []
        if len(account_issues) > 0:
            for compliance in account_issues:
                audit_resource = AuditResource.get_by_id(compliance.audit_resource_id)
                criterion = Criterion.get_by_id(audit_resource.criterion_id)
                status = Status.get_by_id(compliance.status_id)
                issues_list.append(
                    {
                        "compliance": compliance.serialize(),
                        "resource": audit_resource.serialize(),
                        "criterion": criterion.serialize(),
                        "status": status.serialize(),
                    }
                )

        return issues_list

    def get_status_resources_list(self, status_id):
        account_issues = self.get_resources_by_status(status_id)
        issues_list = []
        if len(account_issues) > 0:
            status = Status.get_by_id(status_id)
            for compliance in account_issues:
                audit_resource = AuditResource.get_by_id(compliance.audit_resource_id)
                criterion = Criterion.get_by_id(audit_resource.criterion_id)
                issues_list.append(
                    {
                        "compliance": compliance.serialize(),
                        "resource": audit_resource.serialize(),
                        "criterion": criterion.serialize(),
                        "status": status.serialize(),
                    }
                )

        return issues_list


# This is where we store the results of quering the API
# This should include "green" status checks as well as
# identified risks.
class AuditResource(database_handle.BaseModel):
    criterion_id = peewee.ForeignKeyField(Criterion, backref="audit_resources")
    account_audit_id = peewee.ForeignKeyField(AccountAudit, backref="audit_resources")
    region = peewee.CharField(null=True)
    resource_id = peewee.CharField()
    resource_name = peewee.CharField(null=True)
    resource_persistent_id = peewee.CharField(null=True)
    resource_data = peewee.TextField()
    date_evaluated = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "audit_resource"


class ResourceCompliance(database_handle.BaseModel):
    audit_resource_id = peewee.ForeignKeyField(
        AuditResource, backref="resource_compliance"
    )
    annotation = peewee.TextField(null=True)
    resource_type = peewee.CharField()
    resource_id = peewee.CharField()
    compliance_type = peewee.CharField()
    is_compliant = peewee.BooleanField(default=False)
    is_applicable = peewee.BooleanField(default=True)
    status_id = peewee.ForeignKeyField(Status, backref="status")

    class Meta:
        table_name = "resource_compliance"


# For non-green status issues we record a risk record
class ResourceRiskAssessment(database_handle.BaseModel):
    criterion_id = peewee.ForeignKeyField(
        Criterion, backref="resource_risk_assessments"
    )
    audit_resource_id = peewee.ForeignKeyField(
        AuditResource, backref="resource_risk_assessments"
    )
    account_audit_id = peewee.ForeignKeyField(
        AccountAudit, backref="resource_risk_assessments"
    )
    resource_id = peewee.CharField()
    date_first_identifed = peewee.DateField()
    date_last_notified = peewee.DateField(null=True)
    date_of_review = peewee.DateField(null=True)
    accepted_risk = peewee.BooleanField(default=False)
    analyst_assessed = peewee.BooleanField(default=False)
    severity = peewee.ForeignKeyField(Severity, backref="severity", null=True)

    class Meta:
        table_name = "resource_risk_assessment"


class ResourceException(database_handle.BaseModel):
    resource_persistent_id = peewee.CharField()
    criterion_id = peewee.ForeignKeyField(Criterion, backref="resource_exceptions")
    reason = peewee.CharField()
    account_subscription_id = peewee.ForeignKeyField(
        AccountSubscription, backref="resource_exceptions"
    )
    user_id = peewee.ForeignKeyField(User, backref="resource_exceptions")
    date_created = peewee.DateTimeField(default=datetime.datetime.now)
    date_expires = peewee.DateTimeField()

    class Meta:
        table_name = "resource_exception"

    @classmethod
    def has_active_exception(
        cls, criterion_id, resource_persistent_id, account_subscription_id
    ):
        try:
            now = datetime.datetime.now()
            exception = (
                ResourceException.select()
                .where(
                    ResourceException.resource_persistent_id == resource_persistent_id,
                    ResourceException.criterion_id == criterion_id,
                    ResourceException.account_subscription_id
                    == account_subscription_id,
                    ResourceException.date_created <= now,
                    ResourceException.date_expires >= now,
                )
                .get()
            )

            app.log.debug(
                "Found exception: " + app.utilities.to_json(exception.serialize())
            )

        except peewee.DoesNotExist:
            app.log.debug(app.utilities.get_typed_exception())
            exception = None
        except Exception:
            app.log.error(app.utilities.get_typed_exception())
            exception = None

        return exception

    @classmethod
    def find_exception(
        cls, criterion_id, resource_persistent_id, account_subscription_id
    ):
        try:
            exception = (
                ResourceException.select()
                .where(
                    ResourceException.resource_persistent_id == resource_persistent_id,
                    ResourceException.criterion_id == criterion_id,
                    ResourceException.account_subscription_id
                    == account_subscription_id,
                )
                .get()
            ).raw()

            app.log.debug("Found exception: " + app.utilities.to_json(exception))

            expiry = exception["date_expires"]
            if expiry is not None:
                exception["expiry_day"] = expiry.day
                exception["expiry_month"] = expiry.month
                exception["expiry_year"] = expiry.year

        except Exception:
            app.log.error(app.utilities.get_typed_exception())
            now = datetime.datetime.now()
            expiry = now + datetime.timedelta(days=90)
            exception = {
                "resource_persistent_id": resource_persistent_id,
                "criterion_id": criterion_id,
                "account_subscription_id": account_subscription_id,
                "reason": "",
                "date_created": now,
                "date_expires": expiry,
                "expiry_day": expiry.day,
                "expiry_month": expiry.month,
                "expiry_year": expiry.year,
            }

        return exception


class AccountSshCidrAllowlist(database_handle.BaseModel):
    cidr = peewee.CharField()
    reason = peewee.CharField()
    account_subscription_id = peewee.ForeignKeyField(
        AccountSubscription, backref="ssh_cidr_allowlist"
    )
    user_id = peewee.ForeignKeyField(User, backref="ssh_cidr_allowlist")
    date_created = peewee.DateTimeField(default=datetime.datetime.now)
    date_expires = peewee.DateTimeField()

    class Meta:
        table_name = "account_ssh_cidr_allowlist"

    @classmethod
    def get_validation_schema(cls):
        # pattern of an IPv4 CIDR
        allowlist_pattern = "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}"
        # check for at least 16 bit subnet mask
        return allowlist_pattern

    @classmethod
    def get_defaults(cls, account_subscription_id, user_id):
        now = datetime.datetime.now()
        default_expiry = now + datetime.timedelta(days=90)
        return {
            "cidr": "",
            "reason": "",
            "account_subscription_id": account_subscription_id,
            "user_id": user_id,
            "date_created": now,
            "date_expires": default_expiry,
        }


class CurrentAccountStats(database_handle.BaseModel):
    audit_date = peewee.DateField(primary_key=True)
    account_id = peewee.ForeignKeyField(
        AccountSubscription, field="account_id", backref="current_stats"
    )
    resources = peewee.IntegerField()
    failed = peewee.IntegerField()
    ratio = peewee.FloatField()

    class Meta:
        table_name = "_current_account_stats"


class CurrentSummaryStats(database_handle.BaseModel):
    total_resources = peewee.FloatField()
    total_failures = peewee.FloatField()
    avg_resources_per_account = peewee.FloatField()
    avg_fails_per_account = peewee.FloatField()
    avg_percent_fails_per_account = peewee.FloatField()
    accounts_audited = peewee.IntegerField()
    percent_accounts_audited = peewee.FloatField()

    class Meta:
        table_name = "_current_summary_stats"
        primary_key = peewee.CompositeKey(
            "avg_resources_per_account", "avg_fails_per_account", "accounts_audited"
        )


class DailyAccountStats(database_handle.BaseModel):
    audit_date = peewee.DateField(primary_key=True)
    account_id = peewee.ForeignKeyField(
        AccountSubscription, field="account_id", backref="current_stats"
    )
    resources = peewee.IntegerField()
    failed = peewee.IntegerField()
    ratio = peewee.FloatField()

    class Meta:
        table_name = "_daily_account_stats"


class DailySummaryStats(database_handle.BaseModel):
    audit_date = peewee.DateField(primary_key=True)
    total_resources = peewee.FloatField()
    total_failures = peewee.FloatField()
    avg_resources_per_account = peewee.FloatField()
    avg_fails_per_account = peewee.FloatField()
    avg_percent_fails_per_account = peewee.FloatField()
    accounts_audited = peewee.IntegerField()
    percent_accounts_audited = peewee.FloatField()

    class Meta:
        table_name = "_daily_summary_stats"


class DailyDeltaStats(database_handle.BaseModel):
    audit_date = peewee.DateField(primary_key=True)
    resources_delta = peewee.FloatField()
    failures_delta = peewee.FloatField()
    avg_resources_delta = peewee.FloatField()
    avg_fails_delta = peewee.FloatField()
    avg_percent_fails_delta = peewee.FloatField()
    accounts_audited_delta = peewee.IntegerField()

    class Meta:
        table_name = "_daily_delta_stats"


class MonthlySummaryStats(database_handle.BaseModel):
    audit_year = peewee.IntegerField()
    audit_month = peewee.IntegerField()
    total_resources = peewee.FloatField()
    total_failures = peewee.FloatField()
    avg_resources_per_account = peewee.FloatField()
    avg_fails_per_account = peewee.FloatField()
    avg_percent_fails_per_account = peewee.FloatField()
    accounts_audited = peewee.IntegerField()
    percent_accounts_audited = peewee.FloatField()

    class Meta:
        table_name = "_monthly_summary_stats"
        primary_key = peewee.CompositeKey("audit_year", "audit_month")


class MonthlyDeltaStats(database_handle.BaseModel):
    audit_year = peewee.IntegerField()
    audit_month = peewee.IntegerField()
    resources_delta = peewee.FloatField()
    failures_delta = peewee.FloatField()
    avg_resources_delta = peewee.FloatField()
    avg_fails_delta = peewee.FloatField()
    avg_percent_fails_delta = peewee.FloatField()
    accounts_audited_delta = peewee.IntegerField()

    class Meta:
        table_name = "_monthly_delta_stats"
        primary_key = peewee.CompositeKey("audit_year", "audit_month")


class HealthMetrics(database_handle.BaseModel):
    name = peewee.CharField(unique=True)
    desc = peewee.TextField()
    metric_type = peewee.CharField()
    data = peewee.FloatField()

    class Meta:
        table_name = "_health_metrics"

    @classmethod
    def update_metrics(cls):
        metrics = [
            {
                "name": "csw_percentage_active_current",
                "type": "gauge",
                "desc": "What percentage of active accounts have a complete audit less than 24 hours old?",
            },
            {
                "name": "csw_percentage_completed_audits_7_days",
                "type": "gauge",
                "desc": "What percentage of audits have run and completed in the past 7 days?",
            },
            {
                "name": "csw_percentage_current_false_positive",
                "type": "gauge",
                "desc": "What percentage of identified misconfigurations are labelled as false positives / not to be actioned?",
            },
            {
                "name": "csw_percentage_actioned_resources",
                "type": "gauge",
                "desc": "What percentage of audited resources have been actioned?",
            },
            {
                "name": "csw_average_failing_resource_days",
                "type": "gauge",
                "desc": "What percentage of audited resources have been actioned?",
            },
        ]
        for metric in metrics:
            metric["query"] = cls.load_metric_query(metric["name"])
            app.log.debug(f"Metric {metric['name']}")
            app.log.debug(f"Query: {metric['query']}")
            cls.update_metric_data(metric)

    @classmethod
    def update_metric_data(cls, metric):
        try:
            db = cls._meta.database
            cursor = db.execute_sql(metric["query"])

            for row in cursor.fetchall():
                app.log.debug("Row: " + app.utilities.to_json(row))
                metric["data"] = row[0]

                metric = (
                    cls.insert(
                        name=metric["name"],
                        desc=metric["desc"],
                        metric_type=metric["type"],
                        data=metric["data"],
                    )
                    .on_conflict(conflict_target=[cls.name], preserve=[cls.data])
                    .execute()
                )
        except Exception:
            app.log.error(app.utilities.get_typed_exception())

    @classmethod
    def load_metric_query(cls, metric_name):
        query = ""
        try:
            file_path = f"chalicelib/api/health_metric_queries/{metric_name}.sql"
            abs_path = os.path.join(os.getcwd(), file_path)
            app.log.debug(os.getcwd())
            print(abs_path)
            with open(abs_path, "r") as script:
                query = script.read()
        except Exception:
            app.log.error(app.utilities.get_typed_exception())

        return query


"""
-- TODO - Do we calculate the aggregations or index the tables and aggregate on the fly ? Ares prefers the later
"""
