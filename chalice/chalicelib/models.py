import json
from peewee import Model
from peewee import CharField, TextField, DateField, DateTimeField, BooleanField
from peewee import BigIntegerField, IntegerField, ForeignKeyField
from playhouse.shortcuts import model_to_dict
from datetime import datetime
from chalicelib.database_handle import DatabaseHandle



dbh = DatabaseHandle()
db = dbh.get_handle()


class BaseModel(Model):

    def serialize(self):
        # front end does not need user ID here
        data = model_to_dict(self)

        # data = self.parse_stored_json(data)

        return data

    def parse_stored_json(self, data):

        for field in data:
            if data[field][:1] in ['{','[']:
                try:
                    parsed = json.loads(data[field])
                    data[field] = parsed
                except ValueError:
                    pass

        return data

    class Meta:
        database = db
        schema = "public"


# Create a product team reference table to link AWS
# accounts to the teams who they belong to
class ProductTeam(BaseModel):
    team_name = CharField()
    active = BooleanField()

    class Meta:
        table_name = "product_team"


dbh.add_model("ProductTeam", ProductTeam)


# Create a subscriptions table which designates
# which AWS accounts we should scan
class AccountSubscription(BaseModel):
    account_id = BigIntegerField()
    account_name = CharField()
    product_team_id = ForeignKeyField(ProductTeam, backref='account_subscriptions')
    active = BooleanField()

    class Meta:
        table_name = "account_subscription"


dbh.add_model("AccountSubscription", AccountSubscription)


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
class AccountAudit(BaseModel):
    account_subscription_id = ForeignKeyField(AccountSubscription, backref='account_audits')
    date_started = DateTimeField(default=datetime.now)
    date_updated = DateTimeField(default=datetime.now)
    date_completed = DateTimeField(null=True)
    active_criteria = IntegerField(default=0)
    criteria_processed = IntegerField(default=0)
    criteria_passed = IntegerField(default=0)
    criteria_failed = IntegerField(default=0)
    issues_found = IntegerField(default=0)

    class Meta:
        table_name = "account_audit"


dbh.add_model("AccountAudit", AccountAudit)

class AccountLatestAudit(BaseModel):
    account_subscription_id = ForeignKeyField(AccountSubscription, backref='account_latest_audit')
    account_audit_id = ForeignKeyField(AccountAudit, backref='account_latest_audit')

    class Meta:
        table_name = "account_latest_audit"


dbh.add_model("AccountLatestAudit", AccountLatestAudit)


# eg AWS domain - Trusted Advisor EC2...
# The tool could be extended beyond the scope of AWS
class CriteriaProvider(BaseModel):
    provider_name = CharField()

    class Meta:
        table_name = "criteria_provider"


dbh.add_model("CriteriaProvider", CriteriaProvider)


# eg Trusted Advisor - Security Groups - Specific Ports Unrestricted
# invoke_class_method like describe_trusted_advisor_check_result
class Criterion(BaseModel):
    criterion_name = CharField()
    criteria_provider_id = ForeignKeyField(CriteriaProvider, backref='criteria')
    invoke_class_name = CharField()
    invoke_class_get_data_method = CharField()
    title = TextField()
    description = TextField()
    why_is_it_important = TextField()
    how_do_i_fix_it = TextField()
    active = BooleanField(default=True)
    is_regional = BooleanField(default=True)

    class Meta:
        table_name = "criterion"


dbh.add_model("Criterion", Criterion)


# Primarily for trusted advisor checks specifies arguments that need to be provided
# eg
# language=en
# checkId=HCP4007jGY (for Security Groups - Specific Ports Unrestricted)
class CriterionParams(BaseModel):
    criterion_id = ForeignKeyField(Criterion, backref='criterion_params')
    param_name = CharField()
    param_value = CharField()

    class Meta:
        table_name = "criterion_params"


dbh.add_model("CriterionParams", CriterionParams)


# We may want more statuses than Red/Amber/Green
class Status(BaseModel):
    status_name = CharField()
    description = TextField()

    class Meta:
        table_name = "status"


dbh.add_model("Status", Status)


# For metrics and accepted risks we can associate a severity which
# allows us to float higher value issues to the top
class Severity(BaseModel):
    severity_name = CharField()
    description = TextField()

    class Meta:
        table_name = "severity"


dbh.add_model("Severity", Severity)


# For metrics and accepted risks we can associate a severity which
# allows us to float higher value issues to the top
# notification classes should extend a base Notification class
# and then override a notify method
# This is a stub that will need to be expanded to enable reporting to things like ZenDesk
class NotificationMethod(BaseModel):
    system_name = CharField()
    description = TextField()
    invoke_class_name = CharField()

    class Meta:
        table_name = "notification_method"


dbh.add_model("NotificationMethod", NotificationMethod)


# For each audit if we're querying the same domain and the same
# method for multiple checks (eg ec2 describe-security-groups)
# we can get the data once, store and re-use it rather than calling
# the api to get the same data multiple times.

# If it's part of a separate audit we need to do it again

# It has a generic name since we may choose to get the AWS data
# via splunk in the future or we could broaden the reach of the
# tool to check other vulnerabilities.
class CachedDataResponse(BaseModel):
    criterion_id = ForeignKeyField(Criterion, backref='cached_data_responses')
    account_audit_id = ForeignKeyField(AccountAudit, backref='cached_data_responses')
    invoke_class_name = CharField()
    invoke_class_get_data_method = CharField()
    response = TextField()

    class Meta:
        table_name = "cached_data_response"


dbh.add_model("CachedDataResponse", CachedDataResponse)


class AuditCriterion(BaseModel):
    criterion_id = ForeignKeyField(Criterion, backref='audit_criteria')
    account_audit_id = ForeignKeyField(AccountAudit, backref='audit_criteria')
    regions = IntegerField(default=0)
    resources = IntegerField(default=0)
    tested = IntegerField(default=0)
    passed = IntegerField(default=0)
    failed = IntegerField(default=0)
    ignored = IntegerField(default=0)

    class Meta:
        table_name = "audit_criterion"


dbh.add_model("AuditCriterion", AuditCriterion)


# This is where we store the results of quering the API
# This should include "green" status checks as well as
# identified risks.
class AuditResource(BaseModel):
    criterion_id = ForeignKeyField(Criterion, backref='audit_resources')
    account_audit_id = ForeignKeyField(AccountAudit, backref='audit_resources')
    region = CharField(null=True)
    resource_id = CharField()
    resource_name = CharField(null=True)
    resource_data = TextField()
    date_evaluated = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "audit_resource"


dbh.add_model("AuditResource", AuditResource)


class ResourceCompliance(BaseModel):
    audit_resource_id = ForeignKeyField(AuditResource, backref='resource_compliance')
    annotation = TextField(null=True)
    resource_type = CharField()
    resource_id = CharField()
    compliance_type = CharField()
    is_compliant = BooleanField(default=False)
    is_applicable = BooleanField(default=True)
    status_id = ForeignKeyField(Status, backref='status')

    class Meta:
        table_name = "resource_compliance"


dbh.add_model("ResourceCompliance", ResourceCompliance)


# For non-green status issues we record a risk record
class ResourceRiskAssessment(BaseModel):
    criterion_id = ForeignKeyField(Criterion, backref='resource_risk_assessments')
    audit_resource_id = ForeignKeyField(AuditResource, backref='resource_risk_assessments')
    account_audit_id = ForeignKeyField(AccountAudit, backref='resource_risk_assessments')
    resource_id = CharField()
    date_first_identifed = DateField()
    date_last_notified = DateField(null=True)
    date_of_review = DateField(null=True)
    accepted_risk = BooleanField(default=False)
    analyst_assessed = BooleanField(default=False)
    severity = ForeignKeyField(Severity, backref='severity', null=True)

    class Meta:
        table_name = "resource_risk_assessment"


dbh.add_model("ResourceRiskAssessment", ResourceRiskAssessment)


'''
-- TODO - Do we calculate the aggregations or index the tables and aggregate on the fly ?
'''
