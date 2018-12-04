import datetime

import peewee

from app import app  # used only for logging
from chalicelib import database_handle


# Create a product team reference table to link AWS
# accounts to the teams who they belong to
class ProductTeam(database_handle.BaseModel):
    team_name = peewee.CharField()
    active = peewee.BooleanField()

    class Meta:
        table_name = "product_team"

    def get_team_failed_resources(self):
        team_id = self.id
        team_failed_resources = []
        try:
            accounts = AccountSubscription.select().join(ProductTeam).where(ProductTeam.id == team_id)
        except Exception as err:
            app.log.debug("Failed to get team accounts: " + str(err))
            accounts = []
        for account in accounts:
            if account.active:
                latest = account.get_latest_audit()
                failed_resources = latest.get_audit_failed_resources()
                if len(failed_resources) > 0:
                    resource_data = {
                        "account": account.serialize(),
                        "audit": latest.serialize(),
                        "resources": []
                    }
                    for compliance in failed_resources:
                        audit_resource = AuditResource.get_by_id(compliance.audit_resource_id)
                        criterion = Criterion.get_by_id(audit_resource.criterion_id)
                        status = Status.get_by_id(compliance.status_id)
                        resource_data["resources"].append({
                            "compliance": compliance.serialize(),
                            "resource": audit_resource.serialize(),
                            "criterion": criterion.serialize(),
                            "status": status.serialize()
                        })
                    team_failed_resources.append(resource_data)
        app.log.debug(app.utilities.to_json(team_failed_resources))
        return team_failed_resources

    def get_team_stats(self):
        team_id = self.id
        app.log.debug(f"Get team dashboard for team: {self.team_name}  ({ team_id })")
        team_accounts = AccountSubscription.select().join(ProductTeam).where(ProductTeam.id == team_id)
        for account in team_accounts:
            app.log.debug(account.account_name)
        team_stats = {
            "active_criteria": 0,
            "criteria_processed": 0,
            "criteria_passed": 0,
            "criteria_failed": 0,
            "issues_found": 0
        }
        account_audits = []
        app.log.debug("Got default stats")
        for account in team_accounts:
            app.log.debug("Get account stats for " + account.account_name)
            if account.active:
                latest = account.get_latest_audit()
                if latest is not None:
                    latest_data = latest.serialize()
                    app.log.debug("Latest audit: " + app.utilities.to_json(latest_data))
                    account_data = account.serialize()
                    account_audits.append({
                        "account": account_data,
                        "stats": latest_data
                    })
                    for stat in team_stats:
                        team_stats[stat] += latest_data[stat]
                else:
                    app.log.error("Latest audit not found for account: " + account.id)
        app.log.debug("Team stats: " + app.utilities.to_json(team_stats))
        return {
            "team": team_stats,
            "accounts": account_audits
        }

    def get_active_accounts(self):
        """
        Get the active accounts linked ot the ProductTeam instance
        :return arr AccountSubscription:
        """
        accounts = (AccountSubscription
                    .select()
                    .join(ProductTeam)
                    .where(ProductTeam.id == self.id,
                           ProductTeam.active == True))
        return accounts

    @classmethod
    def get_criteria_stats(cls, teams):
        """
        Collates stats for active criteria across all accounts for a list of teams
        :param teams arr ProductTeam:
        :return dict:
        """
        # TODO: instead of passing the teams as an array, write the method to operate on the team queryset or [self]
        # routes.team_dashboard
        criteria_stats = []
        for criterion in Criterion.select().where(Criterion.active == True):
            team_data = []
            account_data = []
            for team in teams:
                team_stats = {
                    "resources": 0,
                    "tested": 0,
                    "passed": 0,
                    "failed": 0,
                    "ignored": 0
                }
                app.log.debug("Got default criteria stats")
                for account in ProductTeam.get_active_accounts(team):
                    app.log.debug("Get latest account stats for account: " + str(account.id))
                    account_stats = {
                        "resources": 0,
                        "tested": 0,
                        "passed": 0,
                        "failed": 0,
                        "ignored": 0
                    }
                    app.log.debug('Team ID: ' + str(account.product_team_id.id))
                    if account.active and account.product_team_id.id == team.id:
                        latest = account.get_latest_audit()
                        audit_criteria = AuditCriterion.select().join(AccountAudit).where(AccountAudit.id == latest.id)
                        for audit_criterion in audit_criteria:
                            app.log.debug('Criterion ID: ' + str(audit_criterion.criterion_id.id))
                            if audit_criterion.criterion_id.id == criterion.id:
                                audit_criterion_stats = {
                                    "resources": audit_criterion.resources,
                                    "tested": audit_criterion.tested,
                                    "passed": audit_criterion.passed,
                                    "failed": audit_criterion.failed,
                                    "ignored": audit_criterion.ignored
                                }
                                for stat in account_stats:
                                    account_stats[stat] += audit_criterion_stats[stat]
                        account_data.append({
                            "account_subscription": account.serialize(),
                            "stats": account_stats
                        })
                        for stat in team_stats:
                            team_stats[stat] += account_stats[stat]
                team_data.append({
                    "product_team": team.serialize(),
                    "stats": team_stats
                })
            criteria_stats.append({
                "criterion": criterion.serialize(),
                "product_teams": team_data,
                "account_subscriptions": account_data
            })
        return criteria_stats


# Create a subscriptions table which designates
# which AWS accounts we should scan
class AccountSubscription(database_handle.BaseModel):
    account_id = peewee.BigIntegerField()
    account_name = peewee.CharField()
    product_team_id = peewee.ForeignKeyField(ProductTeam, backref='account_subscriptions')
    active = peewee.BooleanField()

    class Meta:
        table_name = "account_subscription"

    def get_latest_audit(self):
        account_id = self.id
        try:
            latest = AccountAudit.select().join(AccountLatestAudit).where(
                AccountLatestAudit.account_subscription_id == account_id
            ).get()
            app.log.debug("Found latest audit: " + app.utilities.to_json(latest.serialize()))
        except AccountLatestAudit.DoesNotExist as err:
            latest = None
            app.log.debug("Failed to get latest audit: " + str(err))
        except Exception as err:
            latest = None
            app.log.debug("Catch generic exception from get_latest_audit: " + str(err))
        return latest


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

    def get_audit_failed_resources(self):
        account_audit_id = self.id
        try:
            return ResourceCompliance.select().join(AuditResource).where(
                AuditResource.account_audit_id == account_audit_id, ResourceCompliance.status_id == 3
            )
        except Exception as err:
            self.app.log.error("Failed to get audit failed resources: " + str(err))
            return []


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
