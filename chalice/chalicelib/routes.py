import json
import os
import re
import urllib
import datetime

from chalice import Response, BadRequestError

from app import app, load_route_services, read_asset
from chalicelib import models
from chalicelib.validators import FormAddResourceException


@app.route('/')
def index():
    load_route_services()
    app.log.debug('INDEX CONTEXT = ' + str(app.lambda_context))
    return Response(**app.templates.render_authorized_template('logged_in.html', app.current_request))


@app.route('/denied')
def index():
    load_route_services()
    return Response(**app.templates.render_authorized_template('denied.html', app.current_request))


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
                        "category": "All Issues",
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
        authed = app.auth.try_login(app.current_request)
        if authed:
            user_data = app.auth.get_login_data()
            user = models.User.find_active_by_email(user_data['email'])
            teams = user.get_my_teams()
        else:
            teams = []

        #teams = models.ProductTeam.select().where(models.ProductTeam.active == True)
        team_list = []
        for team in teams:
            team_stats = team.get_team_stats()
            team_data = {
                "team": team.serialize(),
                "summary": team_stats
            }
            team_list.append(team_data)

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
    # TODO - add check user has access to team
    load_route_services()
    try:

        team = models.ProductTeam.get_by_id(team_id)
        app.log.debug("Team: " + app.utilities.to_json(team))
        criteria_stats = models.ProductTeam.get_criteria_stats([team])
        app.log.debug("Criteria stats: " + app.utilities.to_json(criteria_stats))

        template_data = {
            "team": team.serialize(),
            "team_summary": team.get_team_stats(),
            "criteria_summary": criteria_stats,
            "failed_resources": team.get_team_failed_resources()
        }

        response = app.templates.render_authorized_template(
            'team_dashboard.html',
            app.current_request,
            template_data,
            [team]
        )

    except Exception as err:
        app.log.error("Route: team dashboard error: " + str(err))
        response = app.templates.default_server_error()
    return Response(**response)


@app.route('/team/{id}/status')
def team_status(id):
    team_id = int(id)
    # TODO - add check user has access to team
    load_route_services()
    try:
        team = models.ProductTeam.get_by_id(team_id)
        app.log.debug("Team: " + app.utilities.to_json(team))
        team_stats = team.get_team_stats()
        template_data = {
            "breadcrumbs": [
                {
                    "title": "My teams",
                    "link": "/team"
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
                    "category": "Team Issues",
                    "modifier_class": "passed" if team_stats["all"]["issues_found"] == 0 else "failed"
                }
            },
            "team": team.serialize(),
            "team_summary": team_stats
        }
        response = app.templates.render_authorized_template(
            'team_status.html',
            app.current_request,
            template_data,
            [team]
        )
    except Exception as err:
        app.log.error("Route: team status error: " + str(err))
        response = app.templates.default_server_error()
    return Response(**response)


@app.route('/team/{id}/issues')
def team_issues(id):
    team_id = int(id)
    # TODO - add check user has access to team
    load_route_services()
    try:
        team = models.ProductTeam.get_by_id(team_id)
        app.log.debug("Team: " + app.utilities.to_json(team))
        team_issues = team.get_team_failed_resources()
        template_data = {
            "breadcrumbs": [
                {
                    "title": "My teams",
                    "link": "/team"
                }
            ],
            "team": team.serialize(),
            "account_issues": team_issues
        }
        response = app.templates.render_authorized_template(
            'team_issues.html',
            app.current_request,
            template_data,
            [team]
        )
    except Exception as err:
        app.log.error("Route: team issues error: " + str(err))
        response = app.templates.default_server_error()
    return Response(**response)


@app.route('/account/{id}/status')
def account_status(id):
    account_id = int(id)
    # TODO - add check user has access to account team
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
                        "title": "My teams",
                        "link": "/team"
                    },
                    {
                        "title": team.team_name,
                        "link": f"/team/{team.id}/status"
                    }
                ],
                "audit": latest.serialize(),
                "status": {
                    "audit_completed": {
                        "display_stat": ("Yes" if (latest.date_completed is not None) else "No"),
                        "category": "Audit complete",
                        "modifier_class": "passed" if (latest.date_completed is not None) else "failed"
                    },
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
                        "display_stat": (audit_stats["all"]["passed"] + audit_stats["all"]["ignored"]),
                        "category": "Resources Passed",
                        "modifier_class": "passed" if (audit_stats["all"]["passed"] + audit_stats["all"]["ignored"]) > 0 else "failed"
                    },
                    "resources_failed": {
                        "display_stat": audit_stats["all"]["failed"],
                        "category": "Resources Failed",
                        "modifier_class": "passed" if audit_stats["all"]["failed"] == 0 else "failed"
                    }
                },
                "audit_stats": audit_stats
            }
            response = app.templates.render_authorized_template(
                'audit_status.html',
                app.current_request,
                template_data,
                [account]
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
    # TODO - add check user has access to account team
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
                        "title": "My teams",
                        "link": "/team"
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
                template_data,
                [account]
            )
        else:
            raise Exception(f"No latest audit for account: {account_id}")
    except Exception as err:
        app.log.error("Route: account issues error: " + str(err))
        response = app.templates.default_server_error()
    return Response(**response)


@app.route('/account/{id}/history')
def account_history(id):
    account_id = int(id)
    # TODO - add check user has access to account team
    load_route_services()
    try:
        account = models.AccountSubscription.get_by_id(account_id)
        team = account.product_team_id
        audit_history = account.get_audit_history()
        history_data = []
        for audit in audit_history:
            audit_stats = audit.get_stats()
            history_data.append({
                "audit": audit.serialize(),
                "stats": audit_stats
            })

        template_data = {
            "breadcrumbs": [
                {
                    "title": "My teams",
                    "link": "/team"
                },

                {
                    "title": team.team_name,
                    "link": f"/team/{team.id}/status"
                }
            ],
            "account": account.serialize(),
            "audit_history": history_data
        }
        response = app.templates.render_authorized_template(
            'audit_history.html',
            app.current_request,
            template_data,
            [account]
        )

    except Exception as err:
        app.log.error("Route: account history error: " + str(err))
        response = app.templates.default_server_error()
    return Response(**response)


@app.route('/account/{id}/history/{audit_id}')
def account_status(id, audit_id):
    account_id = int(id)
    # TODO - add check user has access to account team
    audit_id = int(audit_id)
    try:
        load_route_services()
        account = models.AccountSubscription.get_by_id(account_id)
        audit = models.AccountAudit.get_by_id(audit_id)
        team = account.product_team_id
        if audit is not None:
            audit_stats = audit.get_stats()
            template_data = {
                "breadcrumbs": [
                    {
                        "title": "My teams",
                        "link": "/team"
                    },
                    {
                        "title": team.team_name,
                        "link": f"/team/{team.id}/status"
                    },
                    {
                        "title": account.account_name,
                        "link": f"/account/{account.id}/history"
                    }
                ],
                "audit": audit.serialize(),
                "status": {
                    "audit_completed": {
                        "display_stat": ("Yes" if (audit.date_completed is not None) else "No"),
                        "category": "Audit complete",
                        "modifier_class": "passed" if (audit.date_completed is not None) else "failed"
                    },
                    "checks_passed": {
                        "display_stat": audit.criteria_passed,
                        "category": "Checks Passed",
                        "modifier_class": "passed" if audit.criteria_passed > 0 else "failed"
                    },
                    "checks_failed": {
                        "display_stat": audit.criteria_failed,
                        "category": "Checks Failed",
                        "modifier_class": "passed" if audit.criteria_failed == 0 else "failed"
                    },
                    "resources_passed": {
                        "display_stat": (audit_stats["all"]["passed"] + audit_stats["all"]["ignored"]),
                        "category": "Resources Passed",
                        "modifier_class": "passed" if (audit_stats["all"]["passed"] + audit_stats["all"]["ignored"]) > 0 else "failed"
                    },
                    "resources_failed": {
                        "display_stat": audit_stats["all"]["failed"],
                        "category": "Resources Failed",
                        "modifier_class": "passed" if audit_stats["all"]["failed"] == 0 else "failed"
                    }
                },
                "audit_stats": audit_stats
            }
            response = app.templates.render_authorized_template(
                'audit_status.html',
                app.current_request,
                template_data,
                [account]
            )
        else:
            raise Exception(f"No historic audit for account: {account_id}")
    except Exception as err:
        app.log.error("Route: account status error: " + str(err))
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
        # TODO - add check user has access to team

        template_data = {
            "breadcrumbs": [
                {
                    "title": "My teams",
                    "link": "/team"
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
        response = app.templates.render_authorized_template(
            'check_issues.html',
            app.current_request,
            template_data,
            [account]
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
        # TODO - add check user has access to account team

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


@app.route('/resource/{id}/exception',
           methods=['POST'],
           content_types=['application/x-www-form-urlencoded'])
def resource_post_exception(id):
    id = int(id)
    load_route_services()

    try:
        data = urllib.parse.parse_qs(app.current_request.raw_body.decode("utf-8"))

        resource = models.AuditResource.get_by_id(id)
        account = models.AccountSubscription.get_by_id(
            models.AccountAudit.get_by_id(resource.account_audit_id).account_subscription_id
        )
        # TODO - add check user has access to account team

        compliance = (
            models.ResourceCompliance.select().join(models.AuditResource).where(models.AuditResource.id == resource.id)
        ).get()

        exception = models.ResourceException.find_exception(
            resource.criterion_id.id,
            resource.resource_persistent_id,
            account.id
        )

        form = FormAddResourceException()

        is_valid = form.validate(data)

        exception["reason"] = form.data["reason"]
        exception["expiry_day"] = form.data["expiry_components"]["day"]
        exception["expiry_month"] = form.data["expiry_components"]["month"]
        exception["expiry_year"] = form.data["expiry_components"]["year"]

        # json = app.utilities.to_json(data, True)
        # response = app.templates.render_authorized_template(
        #     'debug.html',
        #     app.current_request,
        #     {
        #         "json": json
        #     }
        # )
        mode = "review" if is_valid else "create"

        response = app.templates.render_authorized_template(
            'resource_exception.html',
            app.current_request,
            {
                "team": models.ProductTeam.get_by_id(account.product_team_id).serialize(),
                "account": account.serialize(),
                "resource": resource.serialize(),
                "criterion": models.Criterion.get_by_id(resource.criterion_id).serialize(),
                "compliance": compliance.serialize(),
                "exception": exception,
                "status": models.Status.get_by_id(compliance.status_id).serialize(),
                "mode": mode,
                "errors": form.get_errors()
            }
        )
    except Exception as err:
        app.log.error("Route: resource error: " + str(err))
        response = app.templates.default_server_error()
    return Response(**response)


@app.route('/resource/{id}/exception',
           methods=['POST'],
           content_types=['application/x-www-form-urlencoded'])
def resource_post_exception(id):
    id = int(id)
    load_route_services()

    try:
        data = urllib.parse.parse_qs(app.current_request.raw_body.decode("utf-8"))

        resource = models.AuditResource.get_by_id(id)
        account = models.AccountSubscription.get_by_id(
            models.AccountAudit.get_by_id(resource.account_audit_id).account_subscription_id
        )
        # TODO - add check user has access to account team

        compliance = (
            models.ResourceCompliance.select().join(models.AuditResource).where(models.AuditResource.id == resource.id)
        ).get()

        exception = models.ResourceException.find_exception(
            resource.criterion_id.id,
            resource.resource_persistent_id,
            account.id
        )

        form = FormAddResourceException()

        is_valid = form.validate(data)

        exception["reason"] = form.data["reason"]
        exception["expiry_day"] = form.data["expiry_components"]["day"]
        exception["expiry_month"] = form.data["expiry_components"]["month"]
        exception["expiry_year"] = form.data["expiry_components"]["year"]

        # Save exception
        if is_valid:
            exception_data = models.ResourceException.clean(exception)

            # create an audit_resource record
            resource_exception = models.ResourceException.create(**exception_data)


        # json = app.utilities.to_json(data, True)
        # response = app.templates.render_authorized_template(
        #     'debug.html',
        #     app.current_request,
        #     {
        #         "json": json
        #     }
        # )
        mode = "review" if is_valid else "create"

        response = app.templates.render_authorized_template(
            'resource_exception.html',
            app.current_request,
            {
                "team": models.ProductTeam.get_by_id(account.product_team_id).serialize(),
                "account": account.serialize(),
                "resource": resource.serialize(),
                "criterion": models.Criterion.get_by_id(resource.criterion_id).serialize(),
                "compliance": compliance.serialize(),
                "exception": exception,
                "status": models.Status.get_by_id(compliance.status_id).serialize(),
                "mode": mode,
                "errors": form.get_errors()
            }
        )
    except Exception as err:
        app.log.error("Route: resource error: " + str(err))
        response = app.templates.default_server_error()
    return Response(**response)


@app.route('/resource/{id}/exception')
def resource_exception(id):
    """
    Figure out if data has been posted
    If posted data is valid
    Return default populated exception if not

    :param id:
    :return:
    """
    id = int(id)
    load_route_services()

    try:

        resource = models.AuditResource.get_by_id(id)
        account = models.AccountSubscription.get_by_id(
            models.AccountAudit.get_by_id(resource.account_audit_id).account_subscription_id
        )
        # TODO - add check user has access to account team

        compliance = (
            models.ResourceCompliance.select().join(models.AuditResource).where(models.AuditResource.id == resource.id)
        ).get()

        exception = models.ResourceException.find_exception(
            resource.criterion_id.id,
            resource.resource_persistent_id,
            account.id
        )

        response = app.templates.render_authorized_template(
            'resource_exception.html',
            app.current_request,
            {
                "team": models.ProductTeam.get_by_id(account.product_team_id).serialize(),
                "account": account.serialize(),
                "resource": resource.serialize(),
                "criterion": models.Criterion.get_by_id(resource.criterion_id).serialize(),
                "compliance": compliance.serialize(),
                "exception": exception,
                "status": models.Status.get_by_id(compliance.status_id).serialize(),
                "mode": "create",
                "errors": {}
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


@app.route('/temp-login')
def temp_login():

    try:
        load_route_services()
        env = os.environ['CSW_ENV']

        headers = {
            "Content-Type": "text/plain"
        }
        body = "Trying login"
        code = 200

        if (env != 'prod'):
            csw_client = app.auth.get_ssm_parameter(f"/csw/{env}/credentials/tester/client")
            csw_secret = app.auth.get_ssm_parameter(f"/csw/{env}/credentials/tester/secret")
            req = app.current_request
            qs = req.query_params

            if (csw_client != '[disabled]'
                    and csw_client == qs.get('client')
                    and csw_secret == qs.get('secret')):

                user = models.User.find_active_by_email(qs.get('email')).serialize()

                app.auth.user_jwt = app.auth.get_jwt(user)

                app.auth.cookie = app.auth.generate_cookie_header_val(app.auth.user_jwt)

                headers["Set-Cookie"] = app.auth.cookie

                body = "Logged in"
        else:
            raise Exception("Unauthorised")

    except Exception as err:
        body = "Temporary login failed "+str(err)
        code = 403
        headers = {
            "Content-Type": "text/plain"
        }

    return Response(
        body=body,
        headers=headers,
        status_code=code
    )

# # TO OVERRIDE a route template with the debug template to view the json template data
# data = app.utilities.to_json(template_data, True)
# response = app.templates.render_authorized_template(
#     'debug.html',
#     app.current_request,
#     {
#         "json": data
#     }
# )
