from chalice import Response

from app import app, load_route_services
from chalicelib.collator import Collator
from chalicelib.database_handle import DatabaseHandle
from chalicelib import models


@app.route('/')
def index():
    load_route_services()
    app.log.debug('INDEX CONTEXT = ' + str(app.lambda_context))
    return Response(**app.templates.render_authorized_route_template('/', app.current_request))


@app.route('/overview')
def overview_dashboard():
    load_route_services()
    try:
        dbh = DatabaseHandle(app)
        db = dbh.get_handle()
        db.connect()
        criteria_stats = Collator(app, dbh).get_criteria_stats(
            models.Criterion.select().where(models.Criterion.active == True),
            models.AccountSubscription.select().where(models.AccountSubscription.active == True),
            models.ProductTeam.select().where(models.ProductTeam.active == True)
        )
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
        response = app.templates.render_authorized_route_template(
            '/team',
            app.current_request,
            {
                'teams': [
                    team.serialize() for team in models.ProductTeam.select().where(models.ProductTeam.active == True)
                ]
            }
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
        team = models.ProductTeam.get_by_id(team_id)
        app.log.debug(f"Get team dashboard for team: {team.team_name}  ({ team_id })")
        accounts = models.AccountSubscription.select().join(models.ProductTeam).where(models.ProductTeam.id == team_id)
        for account in accounts:
            app.log.debug(account.account_name)
        team_stats = collator.get_team_stats(accounts)
        app.log.debug("Team stats: " + app.utilities.to_json(team_stats))
        criteria_stats = collator.get_criteria_stats(
            models.Criterion.select().where(models.Criterion.active == True),
            accounts,
            [team]
        )
        app.log.debug("Criteria stats: " + app.utilities.to_json(criteria_stats))
        response = app.templates.render_authorized_route_template(
            '/team/{id}/dashboard',
            app.current_request,
            {
                "team": team.serialize(),
                "team_summary": team_stats,
                "criteria_summary": criteria_stats,
                "failed_resources": collator.get_team_failed_resources(team.id)
            }
        )
    except Exception as err:
        app.log.error("Route: team/x/dashboard error: " + str(err))
        response = {
            "body": str(err)
        }
    return Response(**response)


@app.route('/resource/{id}')
def resource_details(id):
    id = int(id)
    load_route_services()
    db = None
    try:
        dbh = DatabaseHandle(app)
        db = dbh.get_handle()
        db.connect()
        resource = models.AuditResource.get_by_id(id)
        account = models.AccountSubscription.get_by_id(
            models.AccountAudit.get_by_id(resource.account_audit_id).account_subscription_id
        )
        compliance = (
            models.ResourceCompliance.select().join(models.AuditResource).where(models.AuditResource.id == resource.id)
        ).get()
        response = app.templates.render_authorized_route_template(
            '/resource/{id}',
            app.current_request,
            {
                "team": models.ProductTeam.get_by_id(account.product_team_id).serialize(),
                "account": account.serialize(),
                "resource": resource.serialize(),
                "criterion": models.Criterion.get_by_id(resource.criterion_id).serialize(),
                "compliance": compliance.serialize(),
                "status": models.Status.get_by_id(compliance.status_id).serialize()
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


@app.route('/audit')
def audit_list():
    load_route_services()
    # TODO: Base template needs anchor to this route
    return Response(**app.templates.render_authorized_route_template('/audit', app.current_request))


@app.route('/audit/{id}')
def audit_report(id):
    load_route_services()
    return Response(**app.templates.render_authorized_route_template('/audit/{id}', app.current_request))
