import datetime
import peewee
from app import app  # used only for logging
from chalicelib import database_handle

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

