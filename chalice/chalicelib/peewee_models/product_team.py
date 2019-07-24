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
from chalicelib.peewee_models.user import User


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

    def get_team_stats(self):
        team_id = self.id
        app.log.debug(f"Get team dashboard for team: {self.team_name}  ({ team_id })")
        team_accounts = (
            AccountSubscription.select()
            .join(ProductTeam)
            .where(ProductTeam.id == team_id)
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
                    app.log.debug("Latest audit: " + app.utilities.to_json(latest_data))
                    account_data = account.serialize()
                    account_passed = latest.criteria_failed == 0
                    account_status = {
                        "account": account_data,
                        "stats": latest_data,
                        "passed": account_passed,
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

        accounts_set = set(accounts)
        unique_accounts = list(accounts_set)
        return unique_accounts

    @classmethod
    def get_access_settings(cls, role):
        iam_client = GdsIamClient(app)

        users = iam_client.get_role_users(role)
        accounts = cls.get_iam_role_accounts(role)

        team_settings = {
            "users": users,
            "accounts": accounts
        }

        return team_settings

    @classmethod
    def get_all_team_iam_roles(cls):
        # list roles in host account
        iam_client = GdsIamClient(app)
        caller = iam_client.get_caller_details()
        local_audit_session = iam_client.get_chained_session(caller["Account"])
        roles = iam_client.list_roles(local_audit_session)
        team_roles = []
        for role in roles:
            app.log.debug(str(role))
            # the docs are wrong - list_roles does not return tags
            # if "Tags" in role:
            #     tags = iam_client.tag_list_to_dict(role["Tags"])
            if re.match("csw", role["RoleName"], re.IGNORECASE) is not None:
                app.log.debug(role["RoleName"])
                tag_list = iam_client.list_role_tags(local_audit_session, role["RoleName"])
                app.log.debug(str(tag_list))
                tags = iam_client.tag_list_to_dict(tag_list)
                app.log.debug(str(tags))
                # filter by tags
                is_team_role = ("purpose" in tags) and (tags["purpose"] == "csw-team-role")
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

            for email in users:
                found = False
                # Find existing team members in database matching IAM member list and record
                for current_member in team_members:
                    if current_member.user_id.email == email:
                        found = True
                        current_member._processed = True

                # Create member records (and users where required)
                # for IAM defined users not in database
                if not found:
                    try:
                        user = User.select().where(User.email == email)
                    except peewee.DoesNotExist as err:
                        user_data = {
                            "email": email,
                            "name": User.default_username(email),
                            "active": True
                        }
                        user = User.create(**user_data)

                    ProductTeamUser.create(
                        team_id = self,
                        user_id = user
                    )

            # Delete users not defined in IAM Role
            for current_member in team_members:
                if not current_member._processed:
                    current_member.delete_instance()

            processed = True

        except Exception as err:

            app.log.error(app.utilities.get_typed_exception())
            processed = False

        return processed

    def update_accounts(self, team_accounts):

        try:
            default_team = ProductTeam.get(ProductTeam.team_name == 'TBC')
            accounts = (AccountSubscription
                             .select()
                             )

            for account in accounts:
                account_id = str(account.account_id).rjust(12, "0")
                changed = False

                if account_id in team_accounts:
                    # is a member update team_id
                    account.product_team_id = self.id
                    changed = True

                elif account.product_team_id == self.id:
                    # is not a member reset to default team
                    account.product_team_id = default_team
                    changed = True

                if changed:
                    # save if edited
                    account.save()

            processed = True

        except Exception as err:

            app.log.error(app.utitilies.get_typed_exception())
            processed = False

        return processed
