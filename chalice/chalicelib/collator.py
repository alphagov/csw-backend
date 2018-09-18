# aggregators for collating stats across teams and across audit criteria


class Collator():

    def __init__(self, app=None, dbh=None):
        self.app = app
        self.dbh = dbh
        self.app.log.debug("Created Collator instance")

    def set_database_handle(self, dbh):
        self.dbh = dbh

    def get_default_team_stats(self):
        return {
            "active_criteria": 0,
            "criteria_processed": 0,
            "criteria_passed": 0,
            "criteria_failed": 0,
            "issues_found": 0
        }


    def get_default_criteria_stats(self):
        return {
            "resources": 0,
            "tested": 0,
            "passed": 0,
            "failed": 0,
            "ignored": 0
        }


    def get_latest_audit(self, account_id):

        try:
            AccountAudit = self.dbh.get_model("AccountAudit")
            AccountLatestAudit = self.dbh.get_model("AccountLatestAudit")
            query = (AccountAudit.select().join(AccountLatestAudit).where(AccountLatestAudit.account_subscription_id == account_id))

            latest = query.get()
            self.app.log.debug("Found latest audit: " + self.app.utilities.to_json(latest.serialize()))

        except AccountLatestAudit.DoesNotExist as err:
            latest = None
            self.app.log.debug("Failed to get latest audit: " + str(err))
        except Exception as err:
            latest = None
            self.app.log.debug("Catch generic exception from get_latest_audit: " + str(err))

        return latest

    def get_audit_failed_resources(self, account_audit_id):
        try:
            AuditResource = self.dbh.get_model("AuditResource")
            ResourceCompliance = self.dbh.get_model("ResourceCompliance")

            failed_resources = (ResourceCompliance.select().join(AuditResource).where(AuditResource.account_audit_id == account_audit_id, ResourceCompliance.status_id == 3))

        except Exception as err:
            self.app.log.error("Failed to get audit failed resources: " + str(err))
            failed_resources = []

        return failed_resources

    def get_team_accounts(self, team_id):

        try:
            AccountSubscription = self.dbh.get_model("AccountSubscription")
            ProductTeam = self.dbh.get_model("ProductTeam")

            accounts = (AccountSubscription.select().join(ProductTeam).where(ProductTeam.id == team_id))

        except Exception as err:
            self.app.log.debug("Failed to get team accounts: " + str(err))
            accounts = []

        return accounts

    def get_team_failed_resources(self, team_id):

        AuditResource = self.dbh.get_model("AuditResource")

        team_failed_resources = []
        accounts = self.get_team_accounts(team_id)

        for account in accounts:
            if account.active:
                latest = self.get_latest_audit(account.id)
                failed_resources = self.get_audit_failed_resources(latest.id)

                resource_data = {
                    "account": account.serialize(),
                    "audit": latest.serialize(),
                    "resources": []
                }
                for compliance in failed_resources:
                    compliance_data = compliance.serialize()
                    audit_resource = AuditResource.get_by_id(compliance.audit_resource_id)\

                    resource_data.resources.append({
                        "compliance": compliance_data,
                        "resource": audit_resource.serialize()
                    })

                team_failed_resources.append(resource_data)

        self.app.log.debug(self.app.utilities.to_json(team_failed_resources))

        return team_failed_resources

    def get_team_stats(self, team_accounts):

        team_stats = self.get_default_team_stats()
        account_audits = []

        self.app.log.debug("Got default stats")

        for account in team_accounts:

            self.app.log.debug("Get account stats for " + account.account_name)

            if account.active:

                latest = self.get_latest_audit(account.id)

                if latest is not None:
                    latest_data = latest.serialize()

                    self.app.log.debug("Latest audit: " + self.app.utilities.to_json(latest_data))

                    account_data = account.serialize()
                    account_audits.append({
                        "account": account_data,
                        "stats": latest_data
                    })

                    for stat in team_stats:
                        team_stats[stat] += latest_data[stat]

                else:
                    self.app.log.error("Latest audit not found for account: " + account.id)

        return {
            "team": team_stats,
            "accounts": account_audits
        }


    def get_criteria_stats(self, criteria, accounts, teams):

        AccountAudit = self.dbh.get_model("AccountAudit")
        AuditCriterion = self.dbh.get_model("AuditCriterion")

        criteria_stats = []
        for criterion in criteria:
            team_data = []
            account_data = []
            for team in teams:

                team_stats = self.get_default_criteria_stats()

                self.app.log.debug("Got default criteria stats")

                for account in accounts:

                    self.app.log.debug("Get latest account stats for account: " + str(account.id))

                    account_stats = self.get_default_criteria_stats()

                    self.app.log.debug('Team ID: ' + str(account.product_team_id.id))

                    if account.active and account.product_team_id.id == team.id:

                        latest = self.get_latest_audit(account.id)

                        audit_criteria = (AuditCriterion.select().join(AccountAudit).where(AccountAudit.id == latest.id))

                        for audit_criterion in audit_criteria:

                            self.app.log.debug('Criterion ID: ' + str(audit_criterion.criterion_id.id))

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




