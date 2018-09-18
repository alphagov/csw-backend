from chalicelib.database_handle import DatabaseHandle
from chalicelib.collator import Collator


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

        template_data = {
            "team_summary": team_stats,
            "criteria_summary": criteria_stats
        }

        app.log.debug("Criteria stats: " + app.utilities.to_json(criteria_stats))

        response = {
            "body": app.utilities.to_json(template_data)
        }

    except Exception as err:
        app.log.error("Route: team/x/dashboard error: " + str(err))
        response = {
            "body": str(err)
        }

    # response = app.templates.render_authorized_route_template('/team/{id}/dashboard', app.current_request)

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

        template_data = {
            "criteria_summary": criteria_stats
        }

        app.log.debug("Criteria stats: " + app.utilities.to_json(criteria_stats))

        response = {
            "body": app.utilities.to_json(template_data)
        }

    except Exception as err:
        app.log.error("Route: team/x/dashboard error: " + str(err))
        response = {
            "body": str(err)
        }

    # response = app.templates.render_authorized_route_template('/team/{id}/dashboard', app.current_request)

    return response
