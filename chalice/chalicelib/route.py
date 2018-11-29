from chalicelib.database_handle import DatabaseHandle
from chalicelib.collator import Collator


def route_index(app):

    try:
        template = 'logged_in.html'

        response = app.templates.render_authorized_template(
            template,
            app.current_request
        )

    except Exception as err:
        app.log.error("Route: index error: " + str(err))
        response = {
            "body": str(err)
        }

    return response


def route_logout(app):
    try:
        template = 'logged_out.html'

        response = app.templates.render_authorized_template(
            template,
            app.current_request
        )

    except Exception as err:
        app.log.error("Route: logout error: " + str(err))
        response = {
            "body": str(err)
        }

    return response


def route_team_list(app):
    try:
        dbh = DatabaseHandle(app)
        db = dbh.get_handle()
        db.connect()

        ProductTeam = dbh.get_model("ProductTeam")

        teams = (ProductTeam.select().where(ProductTeam.active == True))

        team_list = []
        for team in teams:
            team_list.append(team.serialize())

        template_data = {
            "teams": team_list
        }

        template = "teams.html"

        response = app.templates.render_authorized_template(
            template,
            app.current_request,
            template_data
        )

    except Exception as err:
        app.log.error("Route: team error: " + str(err))
        response = {
            "body": str(err)
        }

    return response


def route_team_dashboard(app, team_id):

    try:
        dbh = DatabaseHandle(app)
        db = dbh.get_handle()
        db.connect()
        collator = Collator(app, dbh)

        ProductTeam = dbh.get_model("ProductTeam")
        AccountSubscription = dbh.get_model("AccountSubscription")
        Criterion = dbh.get_model("Criterion")

        team = ProductTeam.get_by_id(team_id)

        app.log.debug(f"Get team dashboard for team: {team.team_name}  ({ team_id })")

        accounts = (AccountSubscription.select().join(ProductTeam).where(ProductTeam.id == team_id))

        for account in accounts:
            app.log.debug(account.account_name)

        team_stats = collator.get_team_stats(accounts)

        app.log.debug("Team stats: " + app.utilities.to_json(team_stats))

        active_criteria = (Criterion.select().where(Criterion.active == True))
        criteria_stats = collator.get_criteria_stats(active_criteria, accounts, [team])

        failed_resources = collator.get_team_failed_resources(team.id)

        app.log.debug("Criteria stats: " + app.utilities.to_json(criteria_stats))

        template_data = {
            "team": team.serialize(),
            "team_summary": team_stats,
            "criteria_summary": criteria_stats,
            "failed_resources": failed_resources
        }

        template = "team_dashboard.html"

        response = app.templates.render_authorized_template(
            template,
            app.current_request,
            template_data
        )

    except Exception as err:
        app.log.error("Route: team/x/dashboard error: " + str(err))
        response = {
            "body": str(err)
        }

    return response


def route_overview_dashboard(app):
    try:
        dbh = DatabaseHandle(app)
        db = dbh.get_handle()
        db.connect()
        collator = Collator(app, dbh)

        ProductTeam = dbh.get_model("ProductTeam")
        AccountSubscription = dbh.get_model("AccountSubscription")
        Criterion = dbh.get_model("Criterion")

        teams = (ProductTeam.select().where(ProductTeam.active == True))

        accounts = (AccountSubscription.select().where(AccountSubscription.active == True))

        for account in accounts:
            app.log.debug(account.account_name)

        # team_stats = collator.get_team_stats(accounts)
        # app.log.debug("Team stats: " + app.utilities.to_json(team_stats))

        active_criteria = (Criterion.select().where(Criterion.active == True))
        criteria_stats = collator.get_criteria_stats(active_criteria, accounts, teams)

        app.log.debug("Criteria stats: " + app.utilities.to_json(criteria_stats))

        template_data = {
            "criteria_summary": criteria_stats
        }

        template = "overview.html"

        response = app.templates.render_authorized_template(
            template,
            app.current_request,
            template_data
        )

    except Exception as err:
        app.log.error("Route: overview error: " + str(err))
        response = {
            "body": str(err)
        }

    return response


def route_resource_details(app, id):
    db = None
    try:
        dbh = DatabaseHandle(app)
        db = dbh.get_handle()
        db.connect()

        AccountAudit = dbh.get_model("AccountAudit")
        ProductTeam = dbh.get_model("ProductTeam")
        AccountSubscription = dbh.get_model("AccountSubscription")
        AuditResource = dbh.get_model("AuditResource")
        ResourceCompliance = dbh.get_model("ResourceCompliance")
        Criterion = dbh.get_model("Criterion")
        Status = dbh.get_model("Status")

        resource = AuditResource.get_by_id(id)

        audit = AccountAudit.get_by_id(resource.account_audit_id)

        account = AccountSubscription.get_by_id(audit.account_subscription_id)

        team = ProductTeam.get_by_id(account.product_team_id)

        criterion = Criterion.get_by_id(resource.criterion_id)

        compliance = (ResourceCompliance.select().join(AuditResource).where(AuditResource.id == resource.id)).get()

        status = Status.get_by_id(compliance.status_id)

        template_data = {
            "team": team.serialize(),
            "account": account.serialize(),
            "resource": resource.serialize(),
            "criterion": criterion.serialize(),
            "compliance": compliance.serialize(),
            "status": status.serialize()
        }

        template = "resource_details.html"

        response = app.templates.render_authorized_template(
            template,
            app.current_request,
            template_data
        )

    except Exception as err:
        if db is not None:
            db.rollback()

        app.log.error("Route: overview error: " + str(err))

        response = {
            "body": str(err)
        }

    return response
