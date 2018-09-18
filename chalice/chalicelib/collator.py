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
            "issues_found": 0,
            "accounts": []
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


    def get_team_stats(self, team_accounts):

        team_stats = self.get_default_team_stats()

        self.app.log.debug("Got default stats")

        for account in team_accounts:

            self.app.log.debug("Get account stats for " + account.account_name)

            if account.active:

                latest = self.get_latest_audit(account.id)

                if latest is not None:
                    latest_data = latest.serialize()
                    account_data = account.serialize()
                    team_stats["accounts"].append({
                        "account": account_data,
                        "stats": latest_data
                    })

                    self.app.log.debug("Latest audit: " + self.app.utilities.to_json(latest_data))

                    for stat in team_stats:
                        team_stats[stat] += latest_data[stat]

                else:
                    self.app.log.error("Latest audit not found for account: " + account.id)

        return team_stats


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




