import datetime

import peewee

from chalicelib import database_handle


# Create a product team reference table to link AWS
# accounts to the teams who they belong to
class ProductTeam(database_handle.BaseModel):
    team_name = peewee.CharField()
    active = peewee.BooleanField()

    class Meta:
        table_name = "product_team"


# Create a subscriptions table which designates
# which AWS accounts we should scan
class AccountSubscription(database_handle.BaseModel):
    account_id = peewee.BigIntegerField()
    account_name = peewee.CharField()
    product_team_id = peewee.ForeignKeyField(ProductTeam, backref='account_subscriptions')
    active = peewee.BooleanField()

    class Meta:
        table_name = "account_subscription"


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
class AccountAudit(database_handle.BaseModel):
    account_subscription_id = peewee.ForeignKeyField(AccountSubscription, backref='account_audits')
    date_started = peewee.DateTimeField(default=datetime.datetime.now)
    date_updated = peewee.DateTimeField(default=datetime.datetime.now)
    date_completed = peewee.DateTimeField(null=True)
    active_criteria = peewee.IntegerField(default=0)
    criteria_processed = peewee.IntegerField(default=0)
    criteria_passed = peewee.IntegerField(default=0)
    criteria_failed = peewee.IntegerField(default=0)
    issues_found = peewee.IntegerField(default=0)

    class Meta:
        table_name = "account_audit"


class AccountLatestAudit(database_handle.BaseModel):
    account_subscription_id = peewee.ForeignKeyField(AccountSubscription, backref='account_latest_audit')
    account_audit_id = peewee.ForeignKeyField(AccountAudit, backref='account_latest_audit')

    class Meta:
        table_name = "account_latest_audit"


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
    criteria_provider_id = peewee.ForeignKeyField(CriteriaProvider, backref='criteria')
    invoke_class_name = peewee.CharField()
    invoke_class_get_data_method = peewee.CharField()
    title = peewee.TextField()
    description = peewee.TextField()
    why_is_it_important = peewee.TextField()
    how_do_i_fix_it = peewee.TextField()
    active = peewee.BooleanField(default=True)
    is_regional = peewee.BooleanField(default=True)

    class Meta:
        table_name = "criterion"


# Primarily for trusted advisor checks specifies arguments that need to be provided
# eg
# language=en
# checkId=HCP4007jGY (for Security Groups - Specific Ports Unrestricted)
class CriterionParams(database_handle.BaseModel):
    criterion_id = peewee.ForeignKeyField(Criterion, backref='criterion_params')
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
    criterion_id = peewee.ForeignKeyField(Criterion, backref='cached_data_responses')
    account_audit_id = peewee.ForeignKeyField(AccountAudit, backref='cached_data_responses')
    invoke_class_name = peewee.CharField()
    invoke_class_get_data_method = peewee.CharField()
    response = peewee.TextField()

    class Meta:
        table_name = "cached_data_response"


class AuditCriterion(database_handle.BaseModel):
    criterion_id = peewee.ForeignKeyField(Criterion, backref='audit_criteria')
    account_audit_id = peewee.ForeignKeyField(AccountAudit, backref='audit_criteria')
    regions = peewee.IntegerField(default=0)
    resources = peewee.IntegerField(default=0)
    tested = peewee.IntegerField(default=0)
    passed = peewee.IntegerField(default=0)
    failed = peewee.IntegerField(default=0)
    ignored = peewee.IntegerField(default=0)

    class Meta:
        table_name = "audit_criterion"


# This is where we store the results of quering the API
# This should include "green" status checks as well as
# identified risks.
class AuditResource(database_handle.BaseModel):
    criterion_id = peewee.ForeignKeyField(Criterion, backref='audit_resources')
    account_audit_id = peewee.ForeignKeyField(AccountAudit, backref='audit_resources')
    region = peewee.CharField(null=True)
    resource_id = peewee.CharField()
    resource_name = peewee.CharField(null=True)
    resource_data = peewee.TextField()
    date_evaluated = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = "audit_resource"


class ResourceCompliance(database_handle.BaseModel):
    audit_resource_id = peewee.ForeignKeyField(AuditResource, backref='resource_compliance')
    annotation = peewee.TextField(null=True)
    resource_type = peewee.CharField()
    resource_id = peewee.CharField()
    compliance_type = peewee.CharField()
    is_compliant = peewee.BooleanField(default=False)
    is_applicable = peewee.BooleanField(default=True)
    status_id = peewee.ForeignKeyField(Status, backref='status')

    class Meta:
        table_name = "resource_compliance"


# For non-green status issues we record a risk record
class ResourceRiskAssessment(database_handle.BaseModel):
    criterion_id = peewee.ForeignKeyField(Criterion, backref='resource_risk_assessments')
    audit_resource_id = peewee.ForeignKeyField(AuditResource, backref='resource_risk_assessments')
    account_audit_id = peewee.ForeignKeyField(AccountAudit, backref='resource_risk_assessments')
    resource_id = peewee.CharField()
    date_first_identifed = peewee.DateField()
    date_last_notified = peewee.DateField(null=True)
    date_of_review = peewee.DateField(null=True)
    accepted_risk = peewee.BooleanField(default=False)
    analyst_assessed = peewee.BooleanField(default=False)
    severity = peewee.ForeignKeyField(Severity, backref='severity', null=True)

    class Meta:
        table_name = "resource_risk_assessment"


'''
-- TODO - Do we calculate the aggregations or index the tables and aggregate on the fly ? Ares prefers the later
'''
