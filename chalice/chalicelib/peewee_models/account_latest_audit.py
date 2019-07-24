import peewee
from app import app  # used only for logging
from chalicelib import database_handle
from chalicelib.peewee_models.account_subscription import AccountSubscription
from chalicelib.peewee_models.account_audit import AccountAudit


class AccountLatestAudit(database_handle.BaseModel):
    account_subscription_id = peewee.ForeignKeyField(
        AccountSubscription, backref="account_latest_audit"
    )
    account_audit_id = peewee.ForeignKeyField(
        AccountAudit, backref="account_latest_audit"
    )

    class Meta:
        table_name = "account_latest_audit"
