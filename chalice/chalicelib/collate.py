# aggregators for collating stats across teams and across audit criteria


def get_default_audit_stats():
    return {
        "active_criteria": 0,
        "criteria_processed": 0,
        "criteria_analysed": 0,
        "criteria_failed": 0,
        "issues_found": 0
    }


def get_default_criteria_stats():
    return {
        "resources": 0,
        "tested": 0,
        "passed": 0,
        "failed": 0,
        "ignored": 0
    }


def get_team_stats(team_accounts, app, dbh):

    AccountAudit = dbh.get_model("AccountAudit")
    AccountLatestAudit = dbh.get_model("AccountLatestAudit")

    team_stats = get_default_audit_stats()

    for account in team_accounts:
        if account.active:

            latest = (AccountAudit.join(AccountLatestAudit).where(AccountLatestAudit.account_subscription_id == account.id).get())

            latest_data = latest.serialize()

            app.log.debug(app.utilties.to_json(latest_data))

            for stat in team_stats:
                team_stats[stat] += latest_data[stat]

    return team_stats


def get_criteria_stats(criteria, accounts, teams):

    criteria_stats = []
    for criterion in criteria:
        team_data = []
        account_data = []
        for team in teams:

            team_stats = get_default_criteria_stats()

            for account in accounts:

                account_stats = get_default_criteria_stats()

                if account.product_team_id.id == team.id:
                    latest = account.account_latest_audit.account_audit_id
                    audit_criteria = latest.audit_criteria
                    for audit_criterion in audit_criteria:
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
                        "account_subscription": account,
                        "stats": account_stats
                    })

                    for stat in team_stats:
                        team_stats[stat] += account_stats[stat]

            team_data.append({
                "product_team": team,
                "stats": team_stats
            })

        criteria_stats.append({
            "criterion": criterion,
            "product_teams": team_data,
            "account_subscriptions": account_data
        })

    return criteria_stats




