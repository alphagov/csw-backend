import datetime
import peewee
from app import app  # used only for logging
from chalicelib import database_handle
from chalicelib.peewee_models.account_subscription import AccountSubscription


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

    def get_stats(self):

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
                .where(AccountAudit.id == self.id)
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

        stats = {"all": audit_stats, "criteria": criteria_stats}
        return stats


