from chalice import Response

from app import app, load_route_services
from chalicelib.database_handle import DatabaseHandle
from chalicelib.collator import Collator


@app.route('/')
def index():
    load_route_services()
    return Response(**app.templates.render_authorized_route_template('/', app.current_request))


@app.route('/overview')
def overview_dashboard():
    app.log.debug("WTF?!")
    load_route_services()
    try:
        dbh = DatabaseHandle(app)
        db = dbh.get_handle()
        db.connect()
        collator = Collator(app, dbh)
        product_team = dbh.get_model("ProductTeam")
        account_subscription = dbh.get_model("AccountSubscription")
        criterion = dbh.get_model("Criterion")
        teams = (product_team.select().where(product_team.active == True))
        accounts = (account_subscription.select().where(account_subscription.active == True))
        for account in accounts:
            app.log.debug(account.account_name)
        active_criteria = (criterion.select().where(criterion.active == True))
        criteria_stats = collator.get_criteria_stats(active_criteria, accounts, teams)
        app.log.debug("Criteria stats: " + app.utilities.to_json(criteria_stats))
        response = app.templates.render_authorized_route_template(
            '/overview',
            app.current_request,
            {"criteria_summary": criteria_stats}
        )
    except Exception as err:
        app.log.error("Route: overview error: " + str(err))
        response = {
            "body": str(err)
        }
    return Response(**response)


@app.route('/team')
def team_list():
    load_route_services()
    try:
        dbh = DatabaseHandle(app)
        db = dbh.get_handle()
        db.connect()
        product_team = dbh.get_model("ProductTeam")
        team_list = []
        for team in product_team.select().where(product_team.active == True):
            team_list.append(team.serialize())
        response = app.templates.render_authorized_route_template(
            '/team',
            app.current_request,
            {'teams': team_list}
        )
    except Exception as err:
        app.log.error("Route: team error: " + str(err))
        response = {
            "body": str(err)
        }
    return Response(**response)


@app.route('/team/{id}/dashboard')
def team_dashboard(id):
    team_id = int(id)
    load_route_services()
    try:
        dbh = DatabaseHandle(app)
        db = dbh.get_handle()
        db.connect()
        collator = Collator(app, dbh)
        product_team = dbh.get_model("ProductTeam")
        team = product_team.get_by_id(team_id)
        app.log.debug(f"Get team dashboard for team: {team.team_name}  ({ team_id })")
        accounts = dbh.get_model("AccountSubscription").select().join(product_team).where(product_team.id == team_id)
        for account in accounts:
            app.log.debug(account.account_name)
        team_stats = collator.get_team_stats(accounts)
        app.log.debug("Team stats: " + app.utilities.to_json(team_stats))
        criterion = dbh.get_model("Criterion")
        active_criteria = (criterion.select().where(criterion.active == True))
        criteria_stats = collator.get_criteria_stats(active_criteria, accounts, [team])
        failed_resources = collator.get_team_failed_resources(team.id)
        app.log.debug("Criteria stats: " + app.utilities.to_json(criteria_stats))
        response = app.templates.render_authorized_route_template(
            '/team/{id}/dashboard',
            app.current_request,
            {
                "team": team.serialize(),
                "team_summary": team_stats,
                "criteria_summary": criteria_stats,
                "failed_resources": failed_resources
            }
        )
    except Exception as err:
        app.log.error("Route: team/x/dashboard error: " + str(err))
        response = {
            "body": str(err)
        }
    return Response(**response)


@app.route('/resource/{id}')  # TODO: test!
def resource_details(id):
    id = int(id)
    load_route_services()
    db = None
    try:
        dbh = DatabaseHandle(app)
        db = dbh.get_handle()
        db.connect()
        audit_resource = dbh.get_model("AuditResource")
        resource = audit_resource.get_by_id(id)
        audit = dbh.get_model("AccountAudit").get_by_id(resource.account_audit_id)
        account = dbh.get_model("AccountSubscription").get_by_id(audit.account_subscription_id)
        team = dbh.get_model("ProductTeam").get_by_id(account.product_team_id)
        criterion = dbh.get_model("Criterion").get_by_id(resource.criterion_id)
        compliance = (
            dbh.get_model("ResourceCompliance").select().join(audit_resource).where(audit_resource.id == resource.id)
        ).get()
        status = dbh.get_model("Status").get_by_id(compliance.status_id)
        response = app.templates.render_authorized_route_template(
            '/resource/{id}',
            app.current_request,
            {
                "team": team.serialize(),
                "account": account.serialize(),
                "resource": resource.serialize(),
                "criterion": criterion.serialize(),
                "compliance": compliance.serialize(),
                "status": status.serialize()
            }
        )
    except Exception as err:
        if db is not None:
            db.rollback()
        app.log.error("Route: overview error: " + str(err))
        response = {
            "body": str(err)
        }
    return Response(**response)


@app.route('/logout')
def logout():
    load_route_services()
    return Response(**app.templates.render_authorized_route_template('/logout', app.current_request))
