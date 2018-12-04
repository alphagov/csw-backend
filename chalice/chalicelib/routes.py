import json

from chalice import Response, BadRequestError

from app import app, load_route_services, read_asset
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
        criteria_stats = models.ProductTeam.get_criteria_stats(
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
        team = models.ProductTeam.get_by_id(team_id)
        criteria_stats = models.ProductTeam.get_criteria_stats([team])
        app.log.debug("Criteria stats: " + app.utilities.to_json(criteria_stats))
        response = app.templates.render_authorized_route_template(
            '/team/{id}/dashboard',
            app.current_request,
            {
                "team": team.serialize(),
                "team_summary": team.get_team_stats(),
                "criteria_summary": criteria_stats,
                "failed_resources": team.get_team_failed_resources()
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
    try:
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


# ASSET RENDERERS
# TODO This doesn't work for binary file types

@app.route('/assets')
def asset_render_qs():
    load_route_services()
    app.log.debug('asset_render function called by /assets?proxy route')
    try:
        req = app.current_request
        app.log.debug(str(req.uri_params))
        app.log.debug(json.dumps(app.current_request))
        if 'proxy' in req.uri_params:
            proxy = req.uri_params['proxy']
        mime_type = app.utilities.get_mime_type(proxy)
        data = read_asset(proxy)
        return Response(
            body=data,
            status_code=200,
            headers={"Content-Type": mime_type}
        )
    except Exception as e:
        app.log.debug(str(e))
        raise BadRequestError(str(e))


@app.route('/assets/{proxy+}')
def asset_render():
    load_route_services()
    app.log.debug('asset_render function called by /assets/{proxy+} route')
    try:
        req = app.current_request
        app.log.debug(str(req.uri_params))
        if 'proxy' in req.uri_params:
            proxy = req.uri_params['proxy']
        else:
            proxy = req.uri_params['proxy+']
        mime_type = app.utilities.get_mime_type(proxy)
        data = read_asset(proxy)
        return Response(
            body=data,
            status_code=200,
            headers={"Content-Type": mime_type}
        )
    except Exception as e:
        app.log.debug(str(e))
        raise BadRequestError(str(e))
