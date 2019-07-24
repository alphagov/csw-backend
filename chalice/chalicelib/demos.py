"""
TEST ROUTES START HERE - RUN AWS API ON DEMAND
and demo routes with static data

"""

from datetime import datetime
import os

from chalice import Response

from app import app, load_route_services
from chalicelib import models
from chalicelib.template_handler import TemplateHandler


AUDIT = {
    "name": "[User Name]",
    "audits": [
        {
            "name": "[User Name]",
            "id": 1,
            "account_subscription": {
                "account_id": 779799343306,
                "account_name": "gds-digital-security",
            },
            "date_started": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "date_updated": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "date_completed": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "active_criteria": 5,
            "criteria_processed": 5,
            "criteria_analysed": 2,
            "criteria_failed": 3,
            "issues_found": 2,
            "criteria": [
                {
                    "id": 1,
                    "name": "SSH port ingress too open",
                    "tested": False,
                    "why_is_it_important": "Opening ports to the world exposes a greater risk if an SSH key is leaked",
                    "how_do_i_fix_it": (
                        "The SSH port (22) should only be open to known GDS IP addresses including the cabinet "
                        "office VPN"
                    ),
                    "processed": "yes",
                    "status": "fail",
                    "issues": 1,
                    "resources": [
                        {"arn": "arn-1", "status": "pass", "issues": "", "advice": ""},
                        {"arn": "arn-2", "status": "fail", "issues": "", "advice": ""},
                    ],
                },
                {
                    "id": 2,
                    "name": "Security groups with open egress",
                    "tested": False,
                    "why_is_it_important": (
                        "Opening ports to the world exposes a greater risk of data been sent out "
                        "from the service to an unknown location"
                    ),
                    "how_do_i_fix_it": (
                        "The egress rules should specify which ports can be used. Only http(s) should "
                        "be open to the world and through a proxy service so that we can record traffic."
                    ),
                    "processed": "yes",
                    "status": "fail",
                    "issues": 1,
                    "resources": [
                        {"arn": "arn-1", "status": "pass", "issues": "", "advice": ""},
                        {
                            "arn": "arn-2",
                            "status": "fail",
                            "issues": "The security group can connect outbound to anywhere",
                            "advice": "You can remediate this by narrowing the ports or ip ranges.",
                        },
                    ],
                },
            ],
        }
    ],
}


@app.route("/demo")
def demo_index():
    app.dummy_data = AUDIT
    load_route_services()
    response = app.templates.render_authorized_template(
        "logged_in.html", app.current_request, {"name": "[User Name]"}
    )
    return Response(**response)


@app.route("/demo/audit")
def demo_audit_list():
    app.dummy_data = AUDIT
    load_route_services()
    response = app.templates.render_authorized_template(
        "audit_list.html", app.current_request, app.dummy_data
    )
    return Response(**response)


@app.route("/demo/audit/{id}")
def demo_audit_report(id):
    app.dummy_data = AUDIT
    load_route_services()
    app.templates = TemplateHandler(app)
    response = app.templates.render_authorized_template(
        "audit.html", app.current_request, app.dummy_data["audits"][0]
    )
    return Response(**response)


# RUN THE FOLLOWING AWS API ON DEMAND


@app.route("/test/ports_ingress_ssh")
def test_ports_ingress_ssh():
    app.dummy_data = AUDIT
    load_route_services()
    try:
        client = app.utilities.get_class_by_name(
            "chalicelib.criteria.aws_ec2_security_group_ingress_ssh.AwsEc2SecurityGroupIngressSsh"
        )
        ec2 = client(app)
        env = os.environ["CSW_ENV"]
        session = ec2.get_session(
            account="103495720024", role=f"csw-{env}_CstSecurityInspectorRole"
        )
        region = "eu-west-1"
        groups = ec2.get_data(session, **{"region": region})
        for group in groups:
            compliance = ec2.evaluate({}, group, [])
            app.log.debug(app.utilities.to_json(compliance))
            group["resource_compliance"] = compliance
            group["status"] = models.Status.get_by_id(compliance["status_id"])
            group["resource_name"] = group["GroupName"]
            group["resource_id"] = group["GroupId"]
            group["region"] = region
        summary = ec2.summarize(groups)
        template_data = {
            "criterion": models.Criterion.get_by_id(1).serialize(),
            "compliance_summary": summary,
            "compliance_results": groups,
            "tested": True,
        }
        response = app.templates.render_authorized_template(
            "test_evaluation.html", app.current_request, template_data
        )
    except Exception as err:
        response = {"body": str(err)}
    return Response(**response)


@app.route("/test/ports_ingress_open")
def test_ports_ingress_open():
    app.dummy_data = AUDIT
    load_route_services()
    try:
        client = app.utilities.get_class_by_name(
            "chalicelib.criteria.aws_ec2_security_group_ingress_open.AwsEc2SecurityGroupIngressOpen"
        )
        ec2 = client(app)
        env = os.environ["CSW_ENV"]
        session = ec2.get_session(
            account="103495720024", role=f"csw-{env}_CstSecurityInspectorRole"
        )
        params = {"region": "eu-west-1"}
        groups = ec2.get_data(session, **params)
        for group in groups:
            compliance = ec2.evaluate({}, group, [])
            app.log.debug(app.utilities.to_json(compliance))
            group["resource_compliance"] = compliance
        summary = ec2.summarize(groups)
        template_data = app.dummy_data["audits"][0]
        template_data["criteria"][0]["compliance_results"] = groups
        template_data["criteria"][0]["compliance_summary"] = summary
        template_data["criteria"][0]["tested"] = True
        response = app.templates.render_authorized_template(
            "test_evaluation.html", app.current_request, template_data
        )
    except Exception as err:
        response = {"body": str(err)}
    return Response(**response)


@app.route("/test/root_mfa")
def test_root_mfa():
    load_route_services()
    try:
        client = app.utilities.get_class_by_name(
            "chalicelib.criteria.aws_support_root_mfa.AwsSupportRootMfa"
        )
        support = client(app)
        env = os.environ["CSW_ENV"]
        session = support.get_session(
            account="103495720024", role=f"csw-{env}_CstSecurityInspectorRole"
        )
        data = support.get_data(session)
        criterion = {
            "id": 3,
            "criterion_name": "MFA enabled on root user account",
            "description": "Checks whether the root IAM user associated with the AWS account has Multi Factor Authentication enabled.",
            "why_is_it_important": "Without MFA it is easier for someone to gain access to your account",
            "how_do_i_fix_it": "If you have the root credentials for your account enable MFA - otherwise speak to RE",
        }
        for item in data:
            compliance = support.evaluate({}, item, [])
            app.log.debug(app.utilities.to_json(compliance))
            item["resource_compliance"] = compliance
            status = {}
            item["status"] = status
            item.update(support.translate(item))
        summary = support.summarize(data)
        template_data = {
            "criterion": criterion,
            "compliance_summary": summary,
            "compliance_results": data,
            "tested": True,
        }
        response = app.templates.render_authorized_template(
            "test_evaluation.html", app.current_request, template_data
        )
    except Exception as err:
        response = {"body": str(err)}
    return Response(**response)


@app.route("/test/validate_iam_policy", cors=True)
def validate_iam_policy():
    load_route_services()
    try:
        client = app.utilities.get_class_by_name(
            "chalicelib.criteria.aws_iam_validate_inspector_policy.AwsIamValidateInspectorPolicy"
        )
        iam = client(app)
        env = os.environ["CSW_ENV"]
        session = iam.get_session(
            account="103495720024", role=f"csw-{env}_CstSecurityInspectorRole"
        )
        data = iam.get_data(session)
        criterion = {
            "id": 4,
            "criterion_name": "IAM inspector policy is up-to-date",
            "description": "Checks whether the Cloud Security Watch role matches the current definition.",
            "why_is_it_important": "If the role policy doesn't grant the right permissions checks will fail to be processed.",
            "how_do_i_fix_it": "Update the module and re-run the terraform apply to re-deploy the role and policy.",
        }
        for item in data:
            compliance = iam.evaluate({}, item, [])
            item["resource_compliance"] = compliance
            status = {}
            item["status"] = status
            item.update(iam.translate(item))
        summary = iam.summarize(data)
        template_data = {
            "criterion": criterion,
            "compliance_summary": summary,
            "compliance_results": data,
            "tested": True,
        }
        response = app.templates.render_authorized_template(
            "test_evaluation.html", app.current_request, template_data
        )
    except Exception as err:
        response = {"body": str(err)}
    return Response(**response)


@app.route("/test/team_loader")
def team_loader():
    load_route_services()
    try:
        team_roles = models.ProductTeam.get_all_team_iam_roles()
        app.log.debug(str(team_roles))
        for role in team_roles:
            users =

            team = models.ProductTeam.get_by_id(role["TagLookup"]["team_id"])

        json = app.utilities.to_json(team_roles)

        response = app.templates.render_authorized_template("debug.html", app.current_request, {"JSON": json})

    except Exception as err:
        response = {
            "body": app.utilities.get_typed_exception() #"failed: " + str(err)
        }
    return Response(**response)