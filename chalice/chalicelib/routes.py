import json

from chalice import Response, BadRequestError

from app import app, load_route_services, read_asset
from chalicelib import models


@app.route('/')
def index():
    load_route_services()
    app.log.debug('INDEX CONTEXT = ' + str(app.lambda_context))
    return Response(**app.templates.render_authorized_template('logged_in.html', app.current_request))


@app.route('/overview')
def overview_dashboard():
    load_route_services()
    try:
        # criteria_stats = models.ProductTeam.get_criteria_stats(
        #     models.ProductTeam.select().where(models.ProductTeam.active == True)
        # )
        # app.log.debug("Criteria stats: " + app.utilities.to_json(criteria_stats))

        # Create empty template_data in case user is not authenticated
        template_data = {}
        authed = app.auth.try_login(app.current_request)
        if authed:
            user_data = app.auth.get_login_data()
            user = models.User.find_active_by_email(user_data['email'])
            overview_data = user.get_overview_data()

            template_data = {
                # "criteria_summary": criteria_stats,
                "status": {
                    "accounts_passed": {
                        "display_stat": overview_data["all"]["accounts_passed"],
                        "category": "Accounts Passed",
                        "modifier_class": "passed" if overview_data["all"]["accounts_passed"] > 0 else "failed"
                    },
                    "accounts_failed": {
                        "display_stat": overview_data["all"]["accounts_failed"],
                        "category": "Accounts Failed",
                        "modifier_class": "passed" if overview_data["all"]["accounts_failed"] == 0 else "failed"
                    },
                    "accounts_unadited": {
                        "display_stat": overview_data["all"]["accounts_unaudited"],
                        "category": "Accounts Unaudited",
                        "modifier_class": "passed" if overview_data["all"]["accounts_unaudited"] == 0 else "failed"
                    },
                    "accounts_inactive": {
                        "display_stat": overview_data["all"]["accounts_inactive"],
                        "category": "Accounts Inactive",
                        "modifier_class": "passed" if overview_data["all"]["accounts_inactive"] == 0 else "failed"
                    },
                    "issues_found": {
                        "display_stat": overview_data["all"]["issues_found"],
                        "category": "Issues Found",
                        "modifier_class": "passed" if overview_data["all"]["issues_found"] == 0 else "failed"
                    }
                },
                "summaries": overview_data
            }

        # data = app.utilities.to_json(template_data, True)
        # app.log.debug("Criteria stats: " + data)
        # response = app.templates.render_authorized_template(
        #     'debug.html',
        #     app.current_request,
        #     {
        #         "json": data
        #     }
        # )
        response = app.templates.render_authorized_template(
            'overview.html',
            app.current_request,
            template_data
        )
    except Exception as err:
        app.log.error("Route: overview error: " + str(err))
        response = app.templates.default_server_error()
    return Response(**response)


@app.route('/team')
def team_list():
    load_route_services()
    try:
        teams = models.ProductTeam.select().where(models.ProductTeam.active == True)
        team_list = models.ProductTeam.serialize_list(teams)
        template_data = {
            "teams": team_list
        }
        response = app.templates.render_authorized_template(
            'teams.html',
            app.current_request,
            template_data
        )
    except Exception as err:
        app.log.error("Route: team error: " + str(err))
        response = app.templates.default_server_error()
    return Response(**response)


@app.route('/team/{id}/dashboard')
def team_dashboard(id):
    team_id = int(id)
    load_route_services()
    try:
        team = models.ProductTeam.get_by_id(team_id)
        app.log.debug("Team: " + app.utilities.to_json(team))
        criteria_stats = models.ProductTeam.get_criteria_stats([team])
        app.log.debug("Criteria stats: " + app.utilities.to_json(criteria_stats))
        response = app.templates.render_authorized_template(
            'team_dashboard.html',
            app.current_request,
            {
                "team": team.serialize(),
                "team_summary": team.get_team_stats(),
                "criteria_summary": criteria_stats,
                "failed_resources": team.get_team_failed_resources()
            }
        )
    except Exception as err:
        app.log.error("Route: team dashboard error: " + str(err))
        response = app.templates.default_server_error()
    return Response(**response)


@app.route('/team/{id}/status')
def team_status(id):
    team_id = int(id)
    load_route_services()
    try:
        team = models.ProductTeam.get_by_id(team_id)
        app.log.debug("Team: " + app.utilities.to_json(team))
        team_stats = team.get_team_stats()
        template_data = {
            "breadcrumbs": [
                {
                    "title": "Teams",
                    "link": f"/team"
                }
            ],
            "status": {
                "accounts_passed": {
                    "display_stat": team_stats["all"]["accounts_passed"],
                    "category": "Accounts Passed",
                    "modifier_class": "passed" if team_stats["all"]["accounts_passed"] > 0 else "failed"
                },
                "accounts_failed": {
                    "display_stat": team_stats["all"]["accounts_failed"],
                    "category": "Accounts Failed",
                    "modifier_class": "passed" if team_stats["all"]["accounts_failed"] == 0 else "failed"
                },
                "accounts_unadited": {
                    "display_stat": team_stats["all"]["accounts_unaudited"],
                    "category": "Accounts Unaudited",
                    "modifier_class": "passed" if team_stats["all"]["accounts_unaudited"] == 0 else "failed"
                },
                "accounts_inactive": {
                    "display_stat": team_stats["all"]["accounts_inactive"],
                    "category": "Accounts Inactive",
                    "modifier_class": "passed" if team_stats["all"]["accounts_inactive"] == 0 else "failed"
                },
                "issues_found": {
                    "display_stat": team_stats["all"]["issues_found"],
                    "category": "Issues Found",
                    "modifier_class": "passed" if team_stats["all"]["issues_found"] == 0 else "failed"
                }
            },
            "team": team.serialize(),
            "team_summary": team_stats
        }
        # data = app.utilities.to_json(template_data, True)
        # app.log.debug("Criteria stats: " + data)
        # response = app.templates.render_authorized_template(
        #     'debug.html',
        #     app.current_request,
        #     {
        #         "json": data
        #     }
        # )
        response = app.templates.render_authorized_template(
            'team_status.html',
            app.current_request,
            template_data
        )
    except Exception as err:
        app.log.error("Route: team status error: " + str(err))
        response = app.templates.default_server_error()
    return Response(**response)


@app.route('/team/{id}/issues')
def team_issues(id):
    team_id = int(id)
    load_route_services()
    try:
        team = models.ProductTeam.get_by_id(team_id)
        app.log.debug("Team: " + app.utilities.to_json(team))
        team_issues = team.get_team_failed_resources()
        template_data = {
            "team": team.serialize(),
            "issues": team_issues
        }
        # data = app.utilities.to_json(template_data, True)
        # response = app.templates.render_authorized_template(
        #     'debug.html',
        #     app.current_request,
        #     {
        #         "json": data
        #     }
        # )
        response = app.templates.render_authorized_template(
            'team_issues.html',
            app.current_request,
            template_data
        )
    except Exception as err:
        app.log.error("Route: team issues error: " + str(err))
        response = app.templates.default_server_error()
    return Response(**response)


@app.route('/account/{id}/status')
def account_status(id):
    account_id = int(id)
    load_route_services()
    try:
        account = models.AccountSubscription.get_by_id(account_id)
        latest = account.get_latest_audit()
        team = account.product_team_id
        if latest is not None:
            audit_stats = latest.get_stats()
            template_data = {
                "breadcrumbs": [
                    {
                        "title": "Teams",
                        "link": f"/team"
                    },
                    {
                        "title": team.team_name,
                        "link": f"/team/{team.id}/status"
                    }
                ],
                "audit": latest.serialize(),
                "status": {
                    "checks_passed": {
                        "display_stat": latest.criteria_passed,
                        "category": "Checks Passed",
                        "modifier_class": "passed" if latest.criteria_passed > 0 else "failed"
                    },
                    "checks_failed": {
                        "display_stat": latest.criteria_failed,
                        "category": "Checks Failed",
                        "modifier_class": "passed" if latest.criteria_failed == 0 else "failed"
                    },
                    "resources_passed": {
                        "display_stat": (audit_stats["audit"]["passed"] + audit_stats["audit"]["ignored"]),
                        "category": "Resources Passed",
                        "modifier_class": "passed" if (audit_stats["audit"]["passed"] + audit_stats["audit"]["ignored"]) > 0 else "failed"
                    },
                    "resources_failed": {
                        "display_stat": audit_stats["audit"]["failed"],
                        "category": "Resources Failed",
                        "modifier_class": "passed" if audit_stats["audit"]["failed"] == 0 else "failed"
                    }
                },
                "audit_stats": audit_stats
            }
            # data = app.utilities.to_json(template_data, True)
            # response = app.templates.render_authorized_template(
            #     'debug.html',
            #     app.current_request,
            #     {
            #         "json": data
            #     }
            # )
            response = app.templates.render_authorized_template(
                'audit_status.html',
                app.current_request,
                template_data
            )
        else:
            raise Exception(f"No latest audit for account: {account_id}")
    except Exception as err:
        app.log.error("Route: account status error: " + str(err))
        response = app.templates.default_server_error()
    return Response(**response)


@app.route('/account/{id}/issues')
def account_issues(id):
    account_id = int(id)
    load_route_services()
    try:
        account = models.AccountSubscription.get_by_id(account_id)
        latest = account.get_latest_audit()
        team = account.product_team_id
        if latest is not None:
            issues_list = latest.get_issues_list()
            template_data = {
                "breadcrumbs": [
                    {
                        "title": "Teams",
                        "link": f"/team"
                    },

                    {
                        "title": team.team_name,
                        "link": f"/team/{team.id}/status"
                    }
                ],
                "audit": latest.serialize(),
                "issues": issues_list
            }
            response = app.templates.render_authorized_template(
                'audit_issues.html',
                app.current_request,
                template_data
            )
        else:
            raise Exception(f"No latest audit for account: {account_id}")
    except Exception as err:
        app.log.error("Route: account issues error: " + str(err))
        response = app.templates.default_server_error()
    return Response(**response)


@app.route('/check/{id}/issues')
def check_issues(id):
    try:
        load_route_services()
        check_id = int(id)
        audit_check = models.AuditCriterion.get_by_id(check_id)
        issues_list = audit_check.get_issues_list()
        audit = audit_check.account_audit_id
        account = audit.account_subscription_id
        team = account.product_team_id

        template_data = {
            "breadcrumbs": [
                {
                    "title": "Teams",
                    "link": f"/team"
                },
                {
                    "title": team.team_name,
                    "link": f"/team/{team.id}/status"
                },
                {
                    "title": account.account_name,
                    "link": f"/account/{account.id}/status"
                }
            ],
            "audit_check": audit_check.serialize(),
            "issues": issues_list
        }
        # data = app.utilities.to_json(template_data, True)
        # response = app.templates.render_authorized_template(
        #     'debug.html',
        #     app.current_request,
        #     {
        #         "json": data
        #     }
        # )
        response = app.templates.render_authorized_template(
            'check_issues.html',
            app.current_request,
            template_data
        )

    except Exception as err:
        app.log.error("Route: account issues error: " + str(err))
        response = app.templates.default_server_error()
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
        response = app.templates.render_authorized_template(
            'resource_details.html',
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
        app.log.error("Route: resource error: " + str(err))
        response = app.templates.default_server_error()
    return Response(**response)


@app.route('/logout')
def logout():
    load_route_services()
    return Response(**app.templates.render_authorized_template('logged_out.html', app.current_request))


@app.route('/audit')
def audit_list():
    load_route_services()
    # TODO: Base template needs anchor to this route
    return Response(**app.templates.render_authorized_template('audit_list.html', app.current_request))


@app.route('/audit/{id}')
def audit_report(id):
    load_route_services()
    return Response(**app.templates.render_authorized_template('audit.html', app.current_request))


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
