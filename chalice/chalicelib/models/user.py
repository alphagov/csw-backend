import datetime
import peewee
from app import app  # used only for logging
from chalicelib import database_handle


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
        name = email.split("@", 1)[0].replace("\.", " ").title()
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


