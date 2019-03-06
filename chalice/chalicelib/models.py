import datetime

import peewee
# peewee has a validator library but it has a max version of 3.1
# this would mean downgrading our peewee version.
# essentially it provides some simple validators and then
# allows you to create custom validators with a standard method signature
# seemed better to rewrite than downgrade
# from peewee_validates import ModelValidator

from app import app  # used only for logging
from chalicelib import database_handle
from chalicelib.validators import *


class User(database_handle.BaseModel):
    """
    Google OAuth is used to authenticate users to a specified email domain
    We want to further limit the use of this tool to specific users within
    that domain.
    Only people in this table (and marked active) should be allowed to login.
    """
    email = peewee.CharField(unique=True)
    name = peewee.CharField()
    active = peewee.BooleanField()

    class Meta:
        table_name = "user"

    @classmethod
    def find_active_by_email(cls, email):
        """
        Look for a user record with active true and matching the email address

        Raises DoesNotExist
        :param email:
        :return self instance:
        """
        user = cls.get(email=email, active=True)

        return user

    def get_overview_data(self):
        """
        Retrieve overview data about the status of all accounts monitored by CSW
        accessible by the current user
        :return:
        """
        # TODO replace this with a select based on user access team roles
        #teams = ProductTeam.select().where(ProductTeam.active == True)
        teams = self.get_my_teams()

        overview_stats = {
            "accounts_audited": 0,
            "accounts_unaudited": 0,
            "accounts_passed": 0,
            "accounts_failed": 0,
            "accounts_inactive": 0,
            "issues_found": 0
        }
        team_summaries = []
        for team in teams:
            team_stats = team.get_team_stats()
            team_data = {
                "team": team.serialize(),
                "summary": team_stats
            }
            for stat in overview_stats:
                overview_stats[stat] += team_stats["all"][stat]
            team_summaries.append(team_data)

        overview_data = {
            "all": overview_stats,
            "teams": team_summaries
        }
        return overview_data

    def get_my_teams(self):
        """
        Get list of teams for which there is a corresponding ProductTeamUser record
        :return arr ProductTeam:
        """
        try:
            teams = (ProductTeam
                     .select()
                     .join(ProductTeamUser)
                     .where(ProductTeamUser.user_id == self.id))
        except Exception as err:
            app.log.debug("Failed to get team list for current user: " + str(err))
            teams = []
        return teams

    def get_my_accounts(self):
        try:
            accounts = (AccountSubscription
                        .select()
                        .join(ProductTeam)
                        .join(ProductTeamUser)
                        .where(ProductTeamUser.user_id == self.id))
        except Exception as err:
            app.log.debug("Failed to get account list for current user: " + str(err))
            accounts = []
        return accounts


    def get_my_exceptions(self):
        try:
            exceptions = (ResourceException
                        .select()
                        .join(AccountSubscription)
                        .join(ProductTeam)
                        .join(ProductTeamUser)
                        .where(ProductTeamUser.user_id == self.id)
                        .order_by(
                            ProductTeam.team_name,
                            AccountSubscription.account_name,
                            ResourceException.criterion_id
                        ))

            for exception in exceptions:
                exception.audit_resource_id = (AuditResource
                                                .select()
                                                .where(
                                                    AuditResource.resource_persistent_id == exception.resource_persistent_id,
                                                    AuditResource.criterion_id == exception.criterion_id
                                                )
                                                .order_by(AuditResource.id.desc())
                                                .get())

        except Exception as err:
            app.log.debug("Failed to get exception list for current user: " + str(err))
            exceptions = []

        return exceptions

    def get_my_allowlists(self):
        try:
            allowed_ssh_cidrs = (AccountSshCidrAllowlist
                        .select()
                        .join(AccountSubscription)
                        .join(ProductTeam)
                        .join(ProductTeamUser)
                        .where(ProductTeamUser.user_id == self.id)
                        .order_by(
                            ProductTeam.team_name,
                            AccountSubscription.account_name
                        ))

            allowlists = [
                {
                    "type": "ssh_cidrs",
                    "list": allowed_ssh_cidrs
                }
            ]

        except Exception as err:
            app.log.debug("Failed to get allow list for current user: " + str(err))
            allowlists = []

        return allowlists


    def can_access_team(self, team_id):
        try:
            member = (ProductTeamUser
                      .select()
                      .where(
                        ProductTeamUser.user_id == self.id,
                        ProductTeamUser.team_id == team_id)
                      .get())
            has_access = True
        except Exception as err:
            has_access = False
        return has_access

    def can_access_account(self, account_id):
        try:
            member = (AccountSubscription
                      .select()
                      .join(ProductTeam)
                      .join(ProductTeamUser)
                      .where(
                        AccountSubscription.id == account_id,
                        ProductTeamUser.user_id == self.id)
                      .get())
            has_access = True
        except Exception as err:
            has_access = False
        return has_access


class UserSession(database_handle.BaseModel):
    """
    UserSession records login sessions against users so we can track things
    like how often and for how long the tool is being used
    """
    date_opened = peewee.DateTimeField(default=datetime.datetime.now)
    date_accessed = peewee.DateTimeField(default=datetime.datetime.now)
    date_closed = peewee.DateTimeField(null=True)

    user_id = peewee.ForeignKeyField(User, backref='sessions')

    class Meta:
        table_name = "user_session"


    @classmethod
    def start(cls, user):
        """
        Create a new session for the current user

        Raises Exception(Not sure which one)
        :param user:
        :return:
        """

        now = datetime.datetime.now()

        session = cls.create(
            user_id = user,
            date_opened = now,
            date_accessed = now,
            date_closed = None
        )

        return session

    @classmethod
    def accessed(cls, user):
        """
        Update the date_accessed field with the current time

        :param user:
        :return:
        """
        session = cls.get(user_id=user, date_closed=None)

        now = datetime.datetime.now()

        #session.update(date_accessed = now)
        session.date_accessed = now
        session.save()

        return session

    @classmethod
    def close(cls, user):
        """
        Update the current session date_closed with the current time
        :param user:
        :return:
        """
        session = cls.get(user_id=user, date_closed=None)

        now = datetime.datetime.now()

        # session.update(date_accessed=now, date_closed=now)
        session.date_accessed = now
        session.date_closed = now
        session.save()

        return session


class ProductTeam(database_handle.BaseModel):
    """
    Create a product team reference table to link AWS
    accounts to the teams who they belong to
    """
    team_name = peewee.CharField()
    active = peewee.BooleanField()

    class Meta:
        table_name = "product_team"

    def get_item(self):
        return {
            "id": self.id,
            "name": self.team_name
        }

    def user_has_access(self, user):
        """
        Check whether the current user has access to this team
        :param user:
        :return:
        """
        try:
            member = (ProductTeamUser
                      .select()
                      .join(ProductTeam)
                      .where(ProductTeam.id == self.id,
                             ProductTeamUser.user_id == user).get())
            is_member = True
        except Exception as err:
            # If there's no matching record they're not a member - this is not an error.
            is_member = False
        return is_member

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
                if latest is not None:
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
        unaudited_accounts = []
        for account in team_accounts:
            app.log.debug(account.account_name)
        account_stats = {
            "accounts_audited": 0,
            "accounts_unaudited": 0,
            "accounts_passed": 0,
            "accounts_failed": 0,
            "accounts_inactive": 0
        }
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
                    account_passed = (latest.criteria_failed == 0)
                    account_status = {
                        "account": account_data,
                        "stats": latest_data,
                        "passed": account_passed
                    }
                    account_audits.append(account_status)
                    account_stats["accounts_audited"] += 1
                    if account_passed:
                        account_stats["accounts_passed"] += 1
                    else:
                        account_stats["accounts_failed"] += 1
                    for stat in team_stats:
                        team_stats[stat] += latest_data[stat]
                else:
                    app.log.error("Latest audit not found for account: " + str(account.id))
                    account_stats["accounts_unaudited"] += 1
                    unaudited_accounts.append({
                        "account": account.serialize()
                    })
            else:
                account_stats["accounts_inactive"] += 1
        app.log.debug("Team stats: " + app.utilities.to_json(team_stats))
        # add account stats to team stats dictionary
        team_stats.update(account_stats)
        return {
            "all": team_stats,
            "accounts": account_audits,
            "unaudited_accounts": unaudited_accounts
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
                        if latest is not None:
                            # account_stats = latest.get_stats()
                            # account_data.append({
                            #     "account_subscription": account.serialize(),
                            #     "stats": account_stats
                            # })
                            # for stat in team_stats:
                            #     team_stats[stat] += account_stats[stat]

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


class ProductTeamUser(database_handle.BaseModel):
    """
    Link product team records to user accounts in order to limit access
    """
    user_id = peewee.ForeignKeyField(User, backref='sessions')
    team_id = peewee.ForeignKeyField(ProductTeam, backref='account_subscriptions')

    class Meta:
        table_name = "product_team_user"


class AccountSubscription(database_handle.BaseModel):
    """
    Create a subscriptions table which designates
    which AWS accounts we should scan
    """
    account_id = peewee.BigIntegerField()
    account_name = peewee.CharField()
    product_team_id = peewee.ForeignKeyField(ProductTeam, backref='account_subscriptions')
    active = peewee.BooleanField()

    class Meta:
        table_name = "account_subscription"

    def get_item(self):
        return {
            "id": self.id,
            "name": self.account_name,
            "reference": self.account_id
        }

    def user_has_access(self, user):
        # Check whether the user is a member in ProductTeamUser
        try:
            member = (ProductTeamUser
                      .select()
                      .join(ProductTeam)
                      .join(AccountSubscription)
                      .where(AccountSubscription.id == self.id,
                             ProductTeamUser.user_id == user)
                      .get())
            is_member = True
        except Exception as err:
            # If there's no matching record they're not a member - this is not an error.
            is_member = False
        return is_member

    def get_latest_audit(self):
        account_id = self.id
        try:
            latest = AccountAudit.select().join(AccountLatestAudit).where(
                AccountLatestAudit.account_subscription_id == account_id
            ).get()
            app.log.debug("Found latest audit: " + app.utilities.to_json(latest.serialize()))
        except peewee.DoesNotExist as err:
            latest = None
            app.log.debug("Failed to get latest audit: " + str(err))
        except Exception as err:
            latest = None
            app.log.debug("Catch generic exception from get_latest_audit: " + str(err))
        return latest

    def get_audit_history(self):
        account_id = self.id
        try:
            show_last_n_days = 30
            time_limit = datetime.datetime.now() - datetime.timedelta(days=show_last_n_days)
            audit_history = (AccountAudit
                .select()
                .where(
                    AccountAudit.account_subscription_id == account_id,
                    AccountAudit.date_started >= time_limit
                )
                .order_by(AccountAudit.date_started.desc()))
        except peewee.DoesNotExist as err:
            audit_history = []
            app.log.debug("Failed to get audit history: " + str(err))
        except Exception as err:
            audit_history = []
            app.log.debug("Catch generic exception from get_audit_history: " + str(err))
        return audit_history


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

    def get_issues_list(self):
        account_issues = self.get_audit_failed_resources()
        issues_list = []
        if len(account_issues) > 0:
            for compliance in account_issues:
                audit_resource = AuditResource.get_by_id(compliance.audit_resource_id)
                criterion = Criterion.get_by_id(audit_resource.criterion_id)
                status = Status.get_by_id(compliance.status_id)
                issues_list.append({
                    "compliance": compliance.serialize(),
                    "resource": audit_resource.serialize(),
                    "criterion": criterion.serialize(),
                    "status": status.serialize()
                })

        return issues_list

    def get_stats(self):

        audit_stats = {
            "resources": 0,
            "tested": 0,
            "passed": 0,
            "failed": 0,
            "ignored": 0
        }
        criteria_stats = []
        try:
            audit_criteria = AuditCriterion.select().join(AccountAudit).where(AccountAudit.id == self.id)
            for audit_criterion in audit_criteria:
                criterion = Criterion.select().where(Criterion.id == audit_criterion.criterion_id.id)
                app.log.debug('Criterion ID: ' + str(audit_criterion.criterion_id.id))
                if criterion is not None:

                    audit_criterion_stats = audit_criterion.serialize()
                    # Add to stats totals for audit
                    for stat in audit_stats:
                        audit_stats[stat] += audit_criterion_stats[stat]

                    # Append criteria stats with current check results
                    criteria_stats.append(audit_criterion_stats)

        except Exception as err:
            app.log.debug("Catch generic exception from get_stats: " + str(err))

        stats = {
            "all": audit_stats,
            "criteria": criteria_stats
        }
        return stats


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
    # TODO: remove the FK below and its class above, not used
    criteria_provider_id = peewee.ForeignKeyField(CriteriaProvider, backref='criteria')
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
    processed = peewee.BooleanField(default=False)

    class Meta:
        table_name = "audit_criterion"

    def get_failed_resources(self):
        account_audit_id = self.account_audit_id

        try:
            criterion = self.criterion_id

            return (ResourceCompliance.select()
                .join(AuditResource)
                .where(
                    AuditResource.criterion_id == criterion.id,
                    AuditResource.account_audit_id == account_audit_id,
                    ResourceCompliance.status_id == 3
                )
            )
        except Exception as err:
            self.app.log.error("Failed to get audit failed resources: " + str(err))
            return []

    def get_issues_list(self):
        account_issues = self.get_failed_resources()
        issues_list = []
        if len(account_issues) > 0:
            for compliance in account_issues:
                audit_resource = AuditResource.get_by_id(compliance.audit_resource_id)
                criterion = Criterion.get_by_id(audit_resource.criterion_id)
                status = Status.get_by_id(compliance.status_id)
                issues_list.append({
                    "compliance": compliance.serialize(),
                    "resource": audit_resource.serialize(),
                    "criterion": criterion.serialize(),
                    "status": status.serialize()
                })

        return issues_list


# This is where we store the results of quering the API
# This should include "green" status checks as well as
# identified risks.
class AuditResource(database_handle.BaseModel):
    criterion_id = peewee.ForeignKeyField(Criterion, backref='audit_resources')
    account_audit_id = peewee.ForeignKeyField(AccountAudit, backref='audit_resources')
    region = peewee.CharField(null=True)
    resource_id = peewee.CharField()
    resource_name = peewee.CharField(null=True)
    resource_persistent_id = peewee.CharField(null=True)
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


class ResourceException(database_handle.BaseModel):
    resource_persistent_id = peewee.CharField()
    criterion_id = peewee.ForeignKeyField(Criterion, backref='resource_exceptions')
    reason = peewee.CharField()
    account_subscription_id = peewee.ForeignKeyField(AccountSubscription, backref='resource_exceptions')
    user_id = peewee.ForeignKeyField(User, backref='resource_exceptions')
    date_created = peewee.DateTimeField(default=datetime.datetime.now)
    date_expires = peewee.DateTimeField()

    class Meta:
        table_name = "resource_exception"

    @classmethod
    def has_active_exception(cls, criterion_id, resource_persistent_id, account_subscription_id):
        try:
            now = datetime.datetime.now()
            exception = (ResourceException.select()
                .where(
                    ResourceException.resource_persistent_id == resource_persistent_id,
                    ResourceException.criterion_id == criterion_id,
                    ResourceException.account_subscription_id == account_subscription_id,
                    ResourceException.date_created <= now,
                    ResourceException.date_expires >= now
                )
                .get()
            )

            app.log.debug("Found exception: " + app.utilities.to_json(exception.serialize()))

        except Exception as err:
            app.log.debug("Exception not found: " + app.utilities.get_typed_exception(err))
            exception = None

        return exception

    @classmethod
    def find_exception(cls, criterion_id, resource_persistent_id, account_subscription_id):
        try:
            exception = (ResourceException.select()
                .where(
                    ResourceException.resource_persistent_id == resource_persistent_id,
                    ResourceException.criterion_id == criterion_id,
                    ResourceException.account_subscription_id == account_subscription_id
                )
                .get()
            ).raw()

            app.log.debug("Found exception: " + app.utilities.to_json(exception))

            expiry = exception['date_expires']
            if expiry is not None:
                exception['expiry_day'] = expiry.day
                exception['expiry_month'] = expiry.month
                exception['expiry_year'] = expiry.year

        except Exception as err:
            app.log.debug(app.utilities.get_typed_exception(err))
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
                "expiry_year": expiry.year
            }


        return exception


class AccountSshCidrAllowlist(database_handle.BaseModel):
    cidr = peewee.CharField()
    reason = peewee.CharField()
    account_subscription_id = peewee.ForeignKeyField(AccountSubscription, backref='ssh_cidr_allowlist')
    user_id = peewee.ForeignKeyField(User, backref='ssh_cidr_allowlist')
    date_created = peewee.DateTimeField(default=datetime.datetime.now)
    date_expires = peewee.DateTimeField()

    class Meta:
        table_name = "account_ssh_cidr_allowlist"

'''
-- TODO - Do we calculate the aggregations or index the tables and aggregate on the fly ? Ares prefers the later
'''
