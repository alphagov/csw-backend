"""
API LAMBDAS
"""
import os
import re
import json
import datetime

# from peewee import Case, fn
# from botocore.exceptions import ClientError
from chalice import Rate, Response, BadRequestError

from app import app, load_route_services
from chalicelib.database_handle import DatabaseHandle
from chalicelib import models


def read_script(script_path):
    """
    Read a script of SQL and parse into discrete commands by separating at the semi colons.
    """
    try:
        commands = []
        abs_path = os.path.join(os.getcwd(), script_path)
        app.log.debug(os.getcwd())
        print(abs_path)
        with open(abs_path, "r") as script:
            command = ""
            lines = script.readlines()
            for line in lines:
                # Ignore script comments
                if not re.match("^\-{2}", line):
                    # Treat empty lines as breaks between commands
                    if re.match("^\s*$", line):

                        if len(command) > 0:
                            # Only add command to array if it's non-empty
                            commands.append(command)
                            command = ""

                    else:
                        # If non-empty and not a comment then it's part of the previous command
                        command += line
            # If there's no new line at the end of the script
            # then the last command gets missed if you don't do this
            if len(command) > 0:
                commands.append(command)
    except Exception as err:
        print(f"Failed to open script: {script_path}: " + str(err))

    return commands


def execute_update_usage_stats_tables(event, context):
    """
    The summary stats are produced daily as static tables.
    These could be rendered as views or materialized views but since the data is not changing that frequently
    that adds significant processing load for little benefit.
    By regenerating the stats on a schedule we can make the interface much faster and keep the database
    processing load lighter.
    """
    status = 0
    commands = []
    try:
        dbh = DatabaseHandle(app)
        scripts = app.utilities.list_files_from_path("chalicelib/api/sql/", "sql")
        for script in scripts:
            app.log.debug(f"Executing SQL from chalice/{script}")
            commands = read_script(script)
            app.log.debug(json.dumps(commands))
            dbh.execute_commands(commands, "csw")
        status = 1
    except Exception as err:
        app.log.error(
            "Update stats tables error: " + app.utilities.get_typed_exception(err)
        )
    return {"status": status, "commands": commands}


# Usage metrics
# Scheduled lambda for usage metrics
@app.schedule(Rate(24, unit=Rate.HOURS))
def scheduled_update_usage_stats_tables(event):
    """
    The default behaviour is that the stats are generated automatically once every 24 hours
    """
    return execute_update_usage_stats_tables(event, {})


# Manual lambda to trigger the usage metrics update
@app.lambda_function()
def update_usage_stats_tables(event, context):
    """
    For the purposes of testing we can manually regenerate the stats summary tables on demand
    """
    return execute_update_usage_stats_tables(event, context)

# Health metrics
# Manual lambda to trigger the health metrics update
@app.lambda_function()
def update_health_metrics_table(event, context):
    return models.HealthMetrics.update_metrics()


# TODO provide a number of GET only routes
# TODO API authentication | whitelisting?
# /api/[ health | prometheus]/... - for health
# /api/dashboardify/... - for the big screens
# /api/stats/... - for raw json data


@app.route("/api/current/summary")
def route_api_current_summary():
    """
    Overall stats of the results of the latest audit across all teams and accounts
    """
    status_code = 200
    try:
        load_route_services()
        authed = app.auth.try_login(app.current_request)

        if authed:
            current_summary = models.CurrentSummaryStats.select()
            items = models.CurrentSummaryStats.serialize_list(current_summary)
            data = {"status": "ok", "items": items}
        else:
            raise Exception("Unauthorised")
    except Exception as err:
        status_code = 403
        data = {"status": "failed", "message": str(err)}
    json = app.utilities.to_json(data, True)
    response = {
        "body": json,
        "status_code": status_code,
        "headers": {"Content-Type": "application/json"},
    }
    return Response(**response)


@app.route("/api/current/accounts")
def route_api_current_accounts():
    """
    Per account summary of latest audit results
    """
    status_code = 200
    try:
        load_route_services()
        authed = app.auth.try_login(app.current_request)

        if authed:
            current_accounts = models.CurrentAccountStats.select()
            items = models.CurrentAccountStats.serialize_list(current_accounts)
            data = {"status": "ok", "items": items}
        else:
            raise Exception("Unauthorised")
    except Exception as err:
        status_code = 403
        data = {"status": "failed", "message": str(err)}
    json = app.utilities.to_json(data, True)
    response = {
        "body": json,
        "status_code": status_code,
        "headers": {"Content-Type": "application/json"},
    }
    return Response(**response)


@app.route("/api/daily/summary")
def route_api_daily_summary():
    """
    Last 2 weeks summary across all accounts day by day to identify short-term trends
    """
    status_code = 200
    try:
        days = 14
        now = datetime.datetime.now()
        days_ago = now - datetime.timedelta(days=days)
        load_route_services()
        authed = app.auth.try_login(app.current_request)

        if authed:
            daily_summary = (
                models.DailySummaryStats.select()
                .where(models.DailySummaryStats.audit_date > days_ago)
                .order_by(models.DailySummaryStats.audit_date.desc())
            )
            items = models.DailySummaryStats.serialize_list(daily_summary)

            data = {"status": "ok", "items": items}
        else:
            raise Exception("Unauthorised")
    except Exception as err:
        status_code = 403
        data = {"status": "failed", "message": str(err)}
    json = app.utilities.to_json(data, True)
    response = {
        "body": json,
        "status_code": status_code,
        "headers": {"Content-Type": "application/json"},
    }
    return Response(**response)


@app.route("/api/daily/delta")
def route_api_daily_delta():
    """
    Comparison yesterday to today looking for what's changed
    """
    status_code = 200
    try:
        days = 14
        now = datetime.datetime.now()
        days_ago = now - datetime.timedelta(days=days)
        load_route_services()
        authed = app.auth.try_login(app.current_request)

        if authed:
            daily_summary = (
                models.DailyDeltaStats.select()
                .where(models.DailyDeltaStats.audit_date > days_ago)
                .order_by(models.DailyDeltaStats.audit_date.desc())
            )
            items = models.DailyDeltaStats.serialize_list(daily_summary)

            data = {"status": "ok", "items": items}
        else:
            raise Exception("Unauthorised")
    except Exception as err:
        status_code = 403
        data = {"status": "failed", "message": str(err)}
    json = app.utilities.to_json(data, True)
    response = {
        "body": json,
        "status_code": status_code,
        "headers": {"Content-Type": "application/json"},
    }
    return Response(**response)


@app.route("/api/monthly/summary")
def route_api_monthly_summary():
    """
    Average monthly summary to identify longer term trends
    """
    status_code = 200
    try:
        load_route_services()
        authed = app.auth.try_login(app.current_request)

        if authed:
            monthly_summary = models.MonthlySummaryStats.select().order_by(
                models.MonthlySummaryStats.audit_year.desc(),
                models.MonthlySummaryStats.audit_month.desc(),
            )
            items = models.MonthlySummaryStats.serialize_list(monthly_summary)

            data = {"status": "ok", "items": items}
        else:
            raise Exception("Unauthorised")
    except Exception as err:
        status_code = 403
        data = {"status": "failed", "message": str(err)}
    json = app.utilities.to_json(data, True)
    response = {
        "body": json,
        "status_code": status_code,
        "headers": {"Content-Type": "application/json"},
    }
    return Response(**response)


@app.route("/api/monthly/delta")
def route_api_monthly_delta():
    """
    Comparison last month vs this month to show change over time
    """
    status_code = 200
    try:
        load_route_services()
        authed = app.auth.try_login(app.current_request)

        if authed:
            monthly_deltas = models.MonthlyDeltaStats.select().order_by(
                models.MonthlyDeltaStats.audit_year.desc(),
                models.MonthlyDeltaStats.audit_month.desc(),
            )
            items = models.MonthlySummaryStats.serialize_list(monthly_deltas)

            data = {"status": "ok", "items": items}
        else:
            raise Exception("Unauthorised")
    except Exception as err:
        status_code = 403
        data = {"status": "failed", "message": str(err)}
    json = app.utilities.to_json(data, True)
    response = {
        "body": json,
        "status_code": status_code,
        "headers": {"Content-Type": "application/json"},
    }
    return Response(**response)


@app.route("/api/daily/account")
def route_api_daily_account():
    """
    List of stats of the last audits for each account for each day in a given time period
    """
    status_code = 200
    try:
        days = 14
        now = datetime.datetime.now()
        days_ago = now - datetime.timedelta(days=days)
        load_route_services()
        authed = app.auth.try_login(app.current_request)

        if authed:
            daily_account = (
                models.DailyAccountStats.select()
                .where(models.DailyAccountStats.audit_date > days_ago)
                .order_by(models.DailyAccountStats.audit_date.desc())
            )
            items = models.DailyAccountStats.serialize_list(daily_account)

            data = {"status": "ok", "items": items}
        else:
            raise Exception("Unauthorised")
    except Exception as err:
        status_code = 403
        data = {"status": "failed", "message": str(err)}
    json = app.utilities.to_json(data, True)
    response = {
        "body": json,
        "status_code": status_code,
        "headers": {"Content-Type": "application/json"},
    }
    return Response(**response)


@app.route("/api/prometheus/metrics")
def route_api_prometheus_metrics():
    """
    Proof of concept endpoint to expose metric data for Prometheus
    In production we'd need this endpoint to be minimal load so we
    could prepare the data or we could separate into multiple
    endpoints with a single metric per endpoint.

    Example metrics implemented
    Percentage of active accounts with audit in last 24 hours
    Average age of most recent audit
    Failed audits in last 24 hours

    Example metric data
    # HELP go_goroutines Number of goroutines that currently exist.
    # TYPE go_goroutines gauge
    go_goroutines
    35
    """
    status_code = 200
    metric_data = ""
    try:
        metrics = [
            {
                "name": "csw_percentage_active_current",
                "type": "gauge",
                "desc": "Percentage of active accounts which have been audited in the last 24 hours",
                "data": 0,
                "query": (
                    "SELECT "
                        "CAST(SUM(CASE WHEN aa.date_completed IS NOT NULL THEN 1 ELSE 0 END) AS FLOAT)/COUNT(*) as metric_data " 
                    "FROM public.account_subscription AS sub "
                    "LEFT JOIN public.account_audit AS aa "
                    "ON sub.id = aa.account_subscription_id "
                    "WHERE sub.active "
                    "AND (aa.date_completed IS NULL "
                    "   OR age(NOW(), aa.date_completed) < INTERVAL '24 hours')"
                )
            },
            {
                "name": "csw_average_age_of_recent_audit",
                "type": "gauge",
                "desc": "Average age of current audit for active accounts",
                "data": 0,
                "query": (
                    "SELECT " 
                        "AVG(EXTRACT(EPOCH FROM age(NOW(), aa.date_completed))) AS average_age "
                    "FROM public.account_subscription AS sub "
                    "INNER JOIN public.account_latest_audit AS ala "
                    "ON sub.id = ala.account_subscription_id "
                    "INNER JOIN public.account_audit AS aa " 
                    "ON aa.id = ala.account_audit_id "
                    "WHERE aa.date_completed IS NOT NULL "
                    "AND sub.active"
                )
            },
            {
                "name": "csw_failed_audits",
                "type": "gauge",
                "desc": "Percentage of failed audits of active accounts in the last week",
                "data": 0,
                "query": (
                    "SELECT "
                        "CAST(SUM(CASE WHEN aa.date_completed IS NULL THEN 1 ELSE 0 END) AS FLOAT)/COUNT(*) AS metric_data " 
                    "FROM public.account_subscription AS sub " 
                    "LEFT JOIN public.account_audit AS aa " 
                    "ON sub.id = aa.account_subscription_id " 
                    "WHERE sub.active " 
                    "AND (aa.date_completed IS NULL OR age(NOW(), aa.date_completed) < INTERVAL '7 days')"
                )
            }
        ]

        dbh = DatabaseHandle(app)
        db = dbh.get_handle()
        for metric in metrics:
            app.log.debug(f"Metric {metric['name']}")
            app.log.debug(f"Query: {metric['query']}")

            cursor = db.execute_sql(metric["query"])
            for row in cursor.fetchall():
                app.log.debug("Row: " + app.utilities.to_json(row))
                metric["data"] = row[0]

                metric_data += f"# HELP {metric['name']} {metric['desc']}\n"
                metric_data += f"# TYPE {metric['name']} {metric['type']}\n"
                metric_data += f"{metric['name']} {metric['data']}\n"

    except Exception as err:
        status_code = 500

    response = {
        "body": metric_data,
        "status_code": status_code,
        "headers": {"Content-Type": "text/plain"},
    }
    return Response(**response)