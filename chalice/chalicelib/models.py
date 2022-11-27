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
from chalicelib.aws.gds_iam_client import GdsIamClient


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
        # teams = ProductTeam.select().where(ProductTeam.active == True)
        teams = self.get_my_teams()

        overview_stats = {
            "accounts_audited": 0,
            "accounts_unaudited": 0,
            "accounts_passed": 0,
            "accounts_failed": 0,
            "accounts_inactive": 0,
            "issues_found": 0,
        }
        team_summaries = []
        for team in teams:
            team_stats = team.get_team_stats()
            team_data = {"team": team.serialize(), "summary": team_stats}
            for stat in overview_stats:
                overview_stats[stat] += team_stats["all"][stat]
            team_summaries.append(team_data)

        overview_data = {"all": overview_stats, "teams": team_summaries}
        return overview_data

    @classmethod
    def default_username(cls, email):
        """
        Take portion of email before @, replace . with space and uppercase words
        """
        name = email.split("@", 1)[0].replace(".", " ").title()
        return name

    def get_my_teams(self):
        """
        Get list of teams for which there is a corresponding ProductTeamUser record
        :return arr ProductTeam:
        """
        try:
            teams = (
                ProductTeam.select()
                .join(ProductTeamUser)
                .where(ProductTeamUser.user_id == self.id)
            )
        except Exception as err:
            app.log.debug("Failed to get team list for current user: " + str(err))
            teams = []
        return teams

    def get_my_accounts(self):
        try:
            accounts = (
                AccountSubscription.select()
                .join(ProductTeam)
                .join(ProductTeamUser)
                .where(ProductTeamUser.user_id == self.id)
            )
        except Exception as err:
            app.log.debug("Failed to get account list for current user: " + str(err))
            accounts = []
        return accounts

    def get_my_exceptions(self):
        try:
            now = datetime.datetime.now()
            exceptions = (
                ResourceException.select()
                .join(AccountSubscription)
                .join(ProductTeam)
                .join(ProductTeamUser)
                .where(
                    ProductTeamUser.user_id == self.id,
                    ResourceException.date_expires > now,
                )
                .order_by(
                    ProductTeam.team_name,
                    AccountSubscription.account_name,
                    ResourceException.criterion_id,
                )
            )

            for exception in exceptions:
                exception.audit_resource_id = (
                    AuditResource.select()
                    .where(
                        AuditResource.resource_persistent_id
                        == exception.resource_persistent_id,
                        AuditResource.criterion_id == exception.criterion_id,
                    )
                    .order_by(AuditResource.id.desc())
                    .get()
                )

        except Exception as err:
            app.log.debug("Failed to get exception list for current user: " + str(err))
            exceptions = []

        return exceptions

    def get_my_allowlists(self):
        try:
            now = datetime.datetime.now()
            allowed_ssh_cidrs = (
                AccountSshCidrAllowlist.select()
                .join(AccountSubscription)
                .join(ProductTeam)
                .join(ProductTeamUser)
                .where(
                    ProductTeamUser.user_id == self.id,
                    AccountSshCidrAllowlist.date_expires > now,
                )
                .order_by(ProductTeam.team_name, AccountSubscription.account_name)
            )

            ssh_check = (
                Criterion.select()
                .where(
                    Criterion.invoke_class_name
                    == "chalicelib.criteria.aws_ec2_security_group_ingress_ssh.AwsEc2SecurityGroupIngressSsh"
                )
                .get()
            )

            allowlists = [
                {
                    "type": "ssh_cidrs",
                    "check_id": ssh_check.id,
                    "list": allowed_ssh_cidrs,
                }
            ]

        except Exception as err:
            app.log.debug("Failed to get allow list for current user: " + str(err))
            allowlists = []

        return allowlists

    def can_access_team(self, team_id):
        try:
            member = (
                ProductTeamUser.select()
                .where(
                    ProductTeamUser.user_id == self.id,
                    ProductTeamUser.team_id == team_id,
                )
                .get()
            )
            has_access = True
        except Exception as err:
            has_access = False
        return has_access

    def can_access_account(self, account_id):
        try:
            member = (
                AccountSubscription.select()
                .join(ProductTeam)
                .join(ProductTeamUser)
                .where(
                    AccountSubscription.id == account_id,
                    ProductTeamUser.user_id == self.id,
                )
                .get()
            )
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

    user_id = peewee.ForeignKeyField(User, backref="sessions")

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
            user_id=user, date_opened=now, date_accessed=now, date_closed=None
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

        # session.update(date_accessed = now)
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
        return {"id": self.id, "name": self.team_name}

    def user_has_access(self, user):
        """
        Check whether the current user has access to this team
        :param user:
        :return:
        """
        try:
            member = (
                ProductTeamUser.select()
                .join(ProductTeam)
                .where(ProductTeam.id == self.id, ProductTeamUser.user_id == user)
                .get()
            )
            is_member = True
        except Exception as err:
            # If there's no matching record they're not a member - this is not an error.
            is_member = False
        return is_member

    def get_team_failed_resources(self):
        team_id = self.id
        team_failed_resources = []
        try:
            accounts = (
                AccountSubscription.select()
                .join(ProductTeam)
                .where(ProductTeam.id == team_id)
            )
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
                            "resources": [],
                        }
                        for compliance in failed_resources:
                            audit_resource = AuditResource.get_by_id(
                                compliance.audit_resource_id
                            )
                            criterion = Criterion.get_by_id(audit_resource.criterion_id)
                            status = Status.get_by_id(compliance.status_id)
                            resource_data["resources"].append(
                                {
                                    "compliance": compliance.serialize(),
                                    "resource": audit_resource.serialize(),
                                    "criterion": criterion.serialize(),
                                    "status": status.serialize(),
                                }
                            )
                        team_failed_resources.append(resource_data)
        app.log.debug(app.utilities.to_json(team_failed_resources))
        return team_failed_resources

    def get_team_stats(self, max_severity=1):
        team_id = self.id
        app.log.debug(f"Get team dashboard for team: {self.team_name}  ({ team_id })")
        team_accounts = (
            AccountSubscription.select()
            .join(ProductTeam)
            .where(ProductTeam.id == team_id)
            .order_by(
                AccountSubscription.active,
                AccountSubscription.suspended,
                AccountSubscription.account_id
            )
        )
        unaudited_accounts = []
        inactive_accounts = []
        for account in team_accounts:
            app.log.debug(account.account_name)
        account_stats = {
            "accounts_audited": 0,
            "accounts_unaudited": 0,
            "accounts_passed": 0,
            "accounts_failed": 0,
            "accounts_inactive": 0,
        }
        team_stats = {
            "active_criteria": 0,
            "criteria_processed": 0,
            "criteria_passed": 0,
            "criteria_failed": 0,
            "issues_found": 0,
        }
        account_audits = []
        app.log.debug("Got default stats")
        for account in team_accounts:
            app.log.debug("Get account stats for " + account.account_name)
            if account.active:
                latest = account.get_latest_audit()
                if latest is not None:
                    latest_data = latest.serialize()
                    audit_criteria = (
                        AuditCriterion.select()
                        .join(Criterion)
                        .where(
                            AuditCriterion.account_audit_id == latest.id,
                            Criterion.severity <= max_severity
                        )
                    )
                    filtered_stats = {
                        "active_criteria": 0,
                        "criteria_processed": 0,
                        "criteria_passed": 0,
                        "criteria_failed": 0,
                        "issues_found": 0
                    }
                    account_passed = True
                    for audit_criterion in audit_criteria:
                        filtered_stats["active_criteria"] += 1
                        if audit_criterion.processed:
                            filtered_stats["criteria_processed"] += 1
                            if audit_criterion.failed > 0:
                                account_passed = False
                                filtered_stats["criteria_failed"] += 1
                                filtered_stats["issues_found"] += audit_criterion.failed
                            else:
                                filtered_stats["criteria_passed"] += 1

                    app.log.debug("Latest audit: " + app.utilities.to_json(latest_data))
                    account_data = account.serialize()
                    account_status = {
                        "account": account_data,
                        "audit": latest_data,
                        "stats": filtered_stats,
                        "passed": account_passed,
                    }
                    account_audits.append(account_status)
                    account_stats["accounts_audited"] += 1
                    if account_passed:
                        account_stats["accounts_passed"] += 1
                    else:
                        account_stats["accounts_failed"] += 1
                    for stat in team_stats:
                        team_stats[stat] += filtered_stats[stat]
                else:
                    app.log.error(
                        "Latest audit not found for account: " + str(account.id)
                    )
                    account_stats["accounts_unaudited"] += 1
                    unaudited_accounts.append({"account": account.serialize()})
            else:
                account_stats["accounts_inactive"] += 1
                inactive_accounts.append({"account": account.serialize()})

        app.log.debug("Team stats: " + app.utilities.to_json(team_stats))
        # add account stats to team stats dictionary
        team_stats.update(account_stats)
        return {
            "all": team_stats,
            "accounts": account_audits,
            "unaudited_accounts": unaudited_accounts,
            "inactive_accounts": inactive_accounts,
        }

    def get_active_accounts(self):
        """
        Get the active accounts linked ot the ProductTeam instance
        :return arr AccountSubscription:
        """
        accounts = (
            AccountSubscription.select()
            .join(ProductTeam)
            .where(ProductTeam.id == self.id, ProductTeam.active == True)
        )
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
                    "ignored": 0,
                }
                app.log.debug("Got default criteria stats")
                for account in ProductTeam.get_active_accounts(team):
                    app.log.debug(
                        "Get latest account stats for account: " + str(account.id)
                    )
                    account_stats = {
                        "resources": 0,
                        "tested": 0,
                        "passed": 0,
                        "failed": 0,
                        "ignored": 0,
                    }
                    app.log.debug("Team ID: " + str(account.product_team_id.id))
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

                            audit_criteria = (
                                AuditCriterion.select()
                                .join(AccountAudit)
                                .where(AccountAudit.id == latest.id)
                            )
                            for audit_criterion in audit_criteria:
                                app.log.debug(
                                    "Criterion ID: "
                                    + str(audit_criterion.criterion_id.id)
                                )
                                if audit_criterion.criterion_id.id == criterion.id:
                                    audit_criterion_stats = {
                                        "resources": audit_criterion.resources,
                                        "tested": audit_criterion.tested,
                                        "passed": audit_criterion.passed,
                                        "failed": audit_criterion.failed,
                                        "ignored": audit_criterion.ignored,
                                    }
                                    for stat in account_stats:
                                        account_stats[stat] += audit_criterion_stats[
                                            stat
                                        ]
                            account_data.append(
                                {
                                    "account_subscription": account.serialize(),
                                    "stats": account_stats,
                                }
                            )
                            for stat in team_stats:
                                team_stats[stat] += account_stats[stat]

                team_data.append(
                    {"product_team": team.serialize(), "stats": team_stats}
                )
            criteria_stats.append(
                {
                    "criterion": criterion.serialize(),
                    "product_teams": team_data,
                    "account_subscriptions": account_data,
                }
            )
        return criteria_stats

    def get_iam_role(self):
        # list roles in host account
        iam_client = GdsIamClient(app)
        caller = iam_client.get_caller_details()
        local_audit_session = iam_client.get_chained_session(caller["Account"])
        roles = iam_client.list_roles(local_audit_session)
        team_role = None
        for role in roles:
            print(str(role))
            if "Tags" in role:
                tags = iam_client.tag_list_to_dict(role["Tags"])
                # filter by tags
                is_team_role = ("purpose" in tags) and (tags["purpose"] == "csw-team-role")
                is_this_team = ("team_id" in tags) and (tags["team_id"] == str(self.id))
                if is_team_role and is_this_team:
                    team_role = role
        return team_role

    @classmethod
    def make_unique(cls, item_list):
        item_set = set(item_list)
        unique_list = list(item_set)
        return unique_list

    @classmethod
    def get_iam_role_accounts(cls, team_role):
        iam_client = GdsIamClient(app)
        caller = iam_client.get_caller_details()
        local_audit_session = iam_client.get_chained_session(caller["Account"])
        arn = team_role["Arn"]
        arn_components = iam_client.parse_arn_components(arn)
        role_name = arn_components["resource_components"]["name"]
        policies = iam_client.list_attached_role_policies(local_audit_session, role_name)
        accounts = []
        for policy_attachment in policies:
            policy_arn = policy_attachment["PolicyArn"]
            policy_version = iam_client.get_policy_default_version(local_audit_session, policy_arn)
            roles = iam_client.get_assumable_roles(policy_version)
            accounts.extend(iam_client.get_role_accounts(roles))

        return cls.make_unique(accounts)

    @classmethod
    def get_access_settings(cls, role):
        iam_client = GdsIamClient(app)

        users = iam_client.get_role_users(role)

        # read non_aws_users tag if present
        accounts = cls.get_iam_role_accounts(role)

        if "TagLookup" in role:
            if "non_aws_users" in role["TagLookup"]:
                non_aws_users = role["TagLookup"]["non_aws_users"].split(" ")
                users.extend(non_aws_users)

            if "unmonitored_accounts" in role["TagLookup"]:
                unmonitored_accounts = role["TagLookup"]["unmonitored_accounts"].split(" ")
                accounts.extend(unmonitored_accounts)

        team_settings = {
            "users": cls.make_unique(users),
            "accounts": cls.make_unique(accounts)
        }

        return team_settings

    @classmethod
    def get_all_team_iam_roles(cls):
        # list roles in host account
        iam_client = GdsIamClient(app)
        iam_client.get_chain_role_params()
        caller = iam_client.get_caller_details()
        local_audit_session = iam_client.get_chained_session(caller["Account"])
        roles = iam_client.list_roles(local_audit_session)
        team_roles = []
        for role in roles:
            app.log.debug(str(role))
            # the docs are wrong - list_roles does not return tags
            # if "Tags" in role:
            #     tags = iam_client.tag_list_to_dict(role["Tags"])
            if "csw" in role["RoleName"].lower():
                app.log.debug(role["RoleName"])
                tag_list = iam_client.list_role_tags(local_audit_session, role["RoleName"])
                app.log.debug(str(tag_list))
                tags = iam_client.tag_list_to_dict(tag_list)
                app.log.debug(str(tags))
                # filter by tags
                is_team_role = tags.get("purpose", "undefined").lower() == "csw-team-role"
                if is_team_role:
                    role["Tags"] = tag_list
                    role["TagLookup"] = tags
                    role["AccessSettings"] = cls.get_access_settings(role)

                    team_roles.append(role)

        return team_roles

    def update_members(self, users):

        try:
            team_members = (ProductTeamUser
                          .select()
                          .where(ProductTeamUser.team_id == self.id)
                          )

            # Delete users not defined in IAM Role
            for current_member in team_members:
                if current_member.user_id.email not in users:
                    current_member.delete_instance()

            for email in users:
                if email:
                    found = False
                    # Find existing team members in database matching IAM member list and record
                    for current_member in team_members:
                        if current_member.user_id.email == email:
                            found = True

                    # Create member records (and users where required)
                    # for IAM defined users not in database
                    if not found:
                        try:
                            user = User.get(User.email == email)
                        except peewee.DoesNotExist as err:
                            user = User.create(
                                email = email,
                                name = User.default_username(email),
                                active = True
                            )

                        ProductTeamUser.create(
                            team_id = self,
                            user_id = user
                        )

            members_processed = True

        except Exception as err:

            app.log.error(app.utilities.get_typed_exception())
            members_processed = False

        return members_processed

    def update_accounts(self, team_accounts):

        try:
            app.log.debug(str(team_accounts))
            default_team = ProductTeam.get(ProductTeam.team_name == 'TBC')
            accounts = AccountSubscription.select()

            for account in accounts:
                account_id = str(account.account_id).rjust(12, "0")

                if account_id in team_accounts:
                    app.log.debug(f"account: {account_id} is a member of team: {self.id}")
                    # is a member update team_id
                    account.product_team_id = self

                elif account.product_team_id == self.id:
                    app.log.debug(f"account: {account_id} is no longer a member of team: {self.id}")
                    # is not a member reset to default team
                    account.product_team_id = default_team

                if account.is_dirty():
                    account.save()

            accounts_processed = True

        except Exception as err:

            app.log.error(app.utilities.get_typed_exception())
            accounts_processed = False

        return accounts_processed



class ProductTeamUser(database_handle.BaseModel):
    """
    Link product team records to user accounts in order to limit access
    """

    user_id = peewee.ForeignKeyField(User, backref="sessions")
    team_id = peewee.ForeignKeyField(ProductTeam, backref="account_subscriptions")

    class Meta:
        table_name = "product_team_user"


class AccountSubscription(database_handle.BaseModel):
    """
    Create a subscriptions table which designates
    which AWS accounts we should scan
    """

    account_id = peewee.BigIntegerField()
    account_name = peewee.CharField()
    product_team_id = peewee.ForeignKeyField(
        ProductTeam, backref="account_subscriptions"
    )
    active = peewee.BooleanField()
    auditable = peewee.BooleanField()
    suspended = peewee.BooleanField()
    in_organisation = peewee.BooleanField(default=False)

    class Meta:
        table_name = "account_subscription"

    def get_item(self):
        return {"id": self.id, "name": self.account_name, "reference": self.account_id}

    def user_has_access(self, user):
        # Check whether the user is a member in ProductTeamUser
        try:
            member = (
                ProductTeamUser.select()
                .join(ProductTeam)
                .join(AccountSubscription)
                .where(
                    AccountSubscription.id == self.id, ProductTeamUser.user_id == user
                )
                .get()
            )
            is_member = True
        except Exception as err:
            # If there's no matching record they're not a member - this is not an error.
            is_member = False
        return is_member

    def get_latest_audit(self):
        account_id = self.id
        try:
            latest = (
                AccountAudit.select()
                .join(AccountLatestAudit)
                .where(AccountLatestAudit.account_subscription_id == account_id)
                .get()
            )
            app.log.debug(
                "Found latest audit: " + app.utilities.to_json(latest.serialize())
            )
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
            time_limit = datetime.datetime.now() - datetime.timedelta(
                days=show_last_n_days
            )
            audit_history = (
                AccountAudit.select()
                .where(
                    AccountAudit.account_subscription_id == account_id,
                    AccountAudit.date_started >= time_limit,
                )
                .order_by(AccountAudit.date_started.desc())
            )
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
    account_subscription_id = peewee.ForeignKeyField(
        AccountSubscription, backref="account_audits"
    )
    date_started = peewee.DateTimeField(default=datetime.datetime.now)
    date_updated = peewee.DateTimeField(default=datetime.datetime.now)
    date_completed = peewee.DateTimeField(null=True)
    active_criteria = peewee.IntegerField(default=0)
    criteria_processed = peewee.IntegerField(default=0)
    criteria_passed = peewee.IntegerField(default=0)
    criteria_failed = peewee.IntegerField(default=0)
    issues_found = peewee.IntegerField(default=0)
    finished = peewee.BooleanField(default=False)

    class Meta:
        table_name = "account_audit"

    def get_audit_failed_resources(self):
        account_audit_id = self.id
        try:
            return (
                ResourceCompliance.select()
                .join(AuditResource)
                .where(
                    AuditResource.account_audit_id == account_audit_id,
                    ResourceCompliance.status_id == 3,
                )
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
                issues_list.append(
                    {
                        "compliance": compliance.serialize(),
                        "resource": audit_resource.serialize(),
                        "criterion": criterion.serialize(),
                        "status": status.serialize(),
                    }
                )

        return issues_list

    def get_stats(self, max_severity=1):

        audit_stats = {
            "resources": 0,
            "tested": 0,
            "passed": 0,
            "failed": 0,
            "ignored": 0,
        }
        criteria_stats = []
        try:
            audit_criteria = (
                AuditCriterion.select()
                .join(AccountAudit)
                .join(Criterion, on=(AuditCriterion.criterion_id == Criterion.id))
                .where(
                    AccountAudit.id == self.id,
                    Criterion.severity <= max_severity
                )
                .order_by(
                    Criterion.severity.asc(),
                    Criterion.criterion_name.asc()
                )
            )
            for audit_criterion in audit_criteria:
                criterion = Criterion.select().where(
                    Criterion.id == audit_criterion.criterion_id.id
                )
                app.log.debug("Criterion ID: " + str(audit_criterion.criterion_id.id))
                if criterion is not None:

                    audit_criterion_stats = audit_criterion.serialize()
                    # Add to stats totals for audit
                    for stat in audit_stats:
                        audit_stats[stat] += audit_criterion_stats[stat]

                    # Append criteria stats with current check results
                    criteria_stats.append(audit_criterion_stats)

        except Exception as err:
            app.log.debug("Catch generic exception from get_stats: " + str(err))

        stats = {"all": audit_stats, "criteria": criteria_stats, "max_severity": int(max_severity)}
        return stats


class AccountLatestAudit(database_handle.BaseModel):
    account_subscription_id = peewee.ForeignKeyField(
        AccountSubscription, backref="account_latest_audit"
    )
    account_audit_id = peewee.ForeignKeyField(
        AccountAudit, backref="account_latest_audit"
    )

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


class DailyResourceCount(database_handle.BaseModel):
    audit_date = peewee.DateField(primary_key=True)
    audited_accounts = peewee.IntegerField()
    failed = peewee.IntegerField()
    passed = peewee.IntegerField()
    ignored = peewee.IntegerField()

    class Meta:
        table_name = "_daily_resource_count"


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


class MonthlyResourceCount(database_handle.BaseModel):
    audit_year = peewee.IntegerField()
    audit_month = peewee.IntegerField()
    audited_accounts = peewee.FloatField()
    failed = peewee.FloatField()
    passed = peewee.FloatField()
    ignored = peewee.FloatField()

    class Meta:
        table_name = "_monthly_resource_count"
        primary_key = peewee.CompositeKey("audit_year", "audit_month")


class CurrentFailsPerAccountCheckStats(database_handle.BaseModel):
    severity = peewee.IntegerField()
    criterion_id = peewee.ForeignKeyField(Criterion, backref="criterion_fails")
    team_id = peewee.ForeignKeyField(ProductTeam, backref="team_fails")
    account_id = peewee.ForeignKeyField(AccountSubscription,
        field="account_id",
        backref="account_fails"
    )
    issues = peewee.IntegerField()

    class Meta:
        table_name = "_current_fails_per_account_check_stats"
        primary_key = peewee.CompositeKey("criterion_id", "team_id", "account_id")


class CurrentFailsPerTeamCheckStats(database_handle.BaseModel):
    severity = peewee.IntegerField()
    criterion_id = peewee.ForeignKeyField(Criterion, backref="criterion_fails")
    team_id = peewee.ForeignKeyField(ProductTeam, backref="team_fails")
    issues = peewee.IntegerField()

    class Meta:
        table_name = "_current_fails_per_team_check_stats"
        primary_key = peewee.CompositeKey("criterion_id", "team_id")


class CurrentFailsPerCheckStats(database_handle.BaseModel):
    severity = peewee.IntegerField()
    criterion_id = (peewee.ForeignKeyField(Criterion,
        backref="criterion_fails",
        primary_key=True
    ))
    issues = peewee.IntegerField()

    class Meta:
        table_name = "_current_fails_per_check_stats"


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
