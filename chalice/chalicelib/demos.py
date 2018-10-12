from datetime import datetime
import json
from chalicelib.database_handle import DatabaseHandle


def execute_test_ports_ingress_ssh(app, load_route_services):

    try:
        load_route_services()

        dbh = DatabaseHandle(app)

        db = dbh.get_handle()
        db.connect()

        Criterion = dbh.get_model("Criterion")
        Status = dbh.get_model('Status')

        Client = app.utilities.get_class_by_name(
            "chalicelib.criteria.aws_ec2_security_group_ingress_ssh.AwsEc2SecurityGroupIngressSsh"
        )
        ec2 = Client(app)

        session = ec2.get_session(account='103495720024', role='csw-dan_CstSecurityInspectorRole')

        region = 'eu-west-1'

        groups = ec2.get_data(session, **{"region": region})

        criterion = Criterion.get_by_id(1)

        for group in groups:
            compliance = ec2.evaluate({}, group, [])

            app.log.debug(app.utilities.to_json(compliance))

            group['resource_compliance'] = compliance

            status = Status.get_by_id(compliance['status_id'])

            group['status'] = status

            group['resource_name'] = group['GroupName']
            group['resource_id'] = group['GroupId']
            group['region'] = region

        summary = ec2.summarize(groups)

        template_data = {
            "criterion": criterion.serialize(),
            "compliance_summary": summary,
            "compliance_results": groups,
            "tested": True
        }

        response = app.templates.render_authorized_route_template(
            '/test/ports_ingress_ssh',
            app.current_request,
            template_data
        )
    except Exception as err:
        response = {
            "body": str(err)
        }

    return response


def execute_test_ports_ingress_open(app, load_route_services):

    try:
        load_route_services()

        Client = app.utilities.get_class_by_name(
            "chalicelib.criteria.aws_ec2_security_group_ingress_open.AwsEc2SecurityGroupIngressOpen"
        )
        ec2 = Client(app)

        session = ec2.get_session(account='103495720024', role='csw-dan_CstSecurityInspectorRole')

        params = {
            "region": 'eu-west-1'
        }

        groups = ec2.get_data(session, **params)

        for group in groups:

            compliance = ec2.evaluate({}, group, [])

            app.log.debug(app.utilities.to_json(compliance))

            group['resource_compliance'] = compliance

        summary = ec2.summarize(groups)

        template_data = app.dummy_data["audits"][0]
        template_data["criteria"][0]["compliance_results"] = groups
        template_data["criteria"][0]["compliance_summary"] = summary
        template_data["criteria"][0]["tested"] = True

        response = app.templates.render_authorized_route_template(
            '/audit/{id}',
            app.current_request,
            template_data
        )
    except Exception as err:
        response = {
            "body": str(err)
        }

    return response


def execute_test_root_mfa(app, load_route_services):

    try:
        load_route_services()

        Client = app.utilities.get_class_by_name(
            "chalicelib.criteria.aws_support_root_mfa.AwsSupportRootMfa"
        )
        support = Client(app)

        session = support.get_session(
            account='103495720024',
            role='csw-dan_CstSecurityInspectorRole'
        )

        data = support.get_data(session)

        criterion = {
            "id": 3,
            "criterion_name": "MFA enabled on root user account",
            "description": "Checks whether the root IAM user associated with the AWS account has Multi Factor Authentication enabled.",
            "why_is_it_important": "Without MFA it is easier for someone to gain access to your account",
            "how_do_i_fix_it": "If you have the root credentials for your account enable MFA - otherwise speak to RE"
        }

        for item in data:
            compliance = support.evaluate({}, item, [])

            app.log.debug(app.utilities.to_json(compliance))

            item['resource_compliance'] = compliance

            status = {}

            item['status'] = status

            item.update(support.translate(item))

        summary = support.summarize(data)

        template_data = {
            "criterion": criterion,
            "compliance_summary": summary,
            "compliance_results": data,
            "tested": True
        }

        response = app.templates.render_authorized_route_template(
            '/test/ports_ingress_ssh',
            app.current_request,
            template_data
        )
    except Exception as err:
        response = {
            "body": str(err)
        }

    return response


def execute_test_iam_validate_inspector_policy(app, load_route_services):

    try:
        load_route_services()

        Client = app.utilities.get_class_by_name(
            "chalicelib.criteria.aws_iam_validate_inspector_policy.AwsIamValidateInspectorPolicy"
        )
        iam = Client(app)

        session = iam.get_session(
            account='103495720024',
            role='csw-dan_CstSecurityInspectorRole'
        )

        data = iam.get_data(session)

        criterion = {
            "id": 4,
            "criterion_name": "IAM inspector policy is up-to-date",
            "description": "Checks whether the Cloud Security Watch role matches the current definition.",
            "why_is_it_important": "If the role policy doesn't grant the right permissions checks will fail to be processed.",
            "how_do_i_fix_it": "Update the module and re-run the terraform apply to re-deploy the role and policy."
        }

        for item in data:
            compliance = iam.evaluate({}, item, [])

            item['resource_compliance'] = compliance

            status = {}

            item['status'] = status

            item.update(iam.translate(item))

        summary = iam.summarize(data)

        template_data = {
            "criterion": criterion,
            "compliance_summary": summary,
            "compliance_results": data,
            "tested": True
        }

        response = app.templates.render_authorized_route_template(
            '/test/validate_iam_policy',
            app.current_request,
            template_data
        )

    except Exception as err:
        response = {
            "body": str(err)
        }

    return response


audit = {
    "name": "[User Name]",
    "audits": [
        {
            "name": "[User Name]",
            "id": 1,
            "account_subscription": {
                "account_id": 779799343306,
                "account_name": "gds-digital-security"
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
                        {
                            "arn": "arn-1",
                            "status": "pass",
                            "issues": "",
                            "advice": ""
                        },
                        {
                            "arn": "arn-2",
                            "status": "fail",
                            "issues": "",
                            "advice": ""
                        }
                    ]
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
                        {
                            "arn": "arn-1",
                            "status": "pass",
                            "issues": "",
                            "advice": ""
                        },
                        {
                            "arn": "arn-2",
                            "status": "fail",
                            "issues": "The security group can connect outbound to anywhere",
                            "advice": "You can remediate this by narrowing the ports or ip ranges."
                        }
                    ]
                }
            ]
        }
    ]
}
