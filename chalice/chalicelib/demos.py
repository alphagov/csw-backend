from datetime import datetime
from chalicelib.database_handle import DatabaseHandle


def execute_test_ports_ingress_ssh(app, load_route_services):

    try:
        load_route_services()

        Client = app.utilities.get_class_by_name(
            "chalicelib.criteria.aws_ec2_security_group_ingress_ssh.AwsEc2SecurityGroupIngressSsh"
        )
        ec2 = Client(app)

        session = ec2.get_session(account='103495720024', role='csw-dan_CstSecurityInspectorRole')

        region = 'eu-west-1'

        groups = ec2.describe_security_groups(session, **{"region": region})

        for group in groups:
            compliance = ec2.evaluate({}, group, [])

            app.log.debug(app.utilities.to_json(compliance))

            group['resource_compliance'] = compliance

            group['resource_name'] = group['GroupName']
            group['resource_id'] = group['GroupId']
            group['region'] = region

        summary = ec2.summarize(groups)

        #template_data = app.dummy_data["audits"][0]
        #template_data["criteria"][0]["compliance_results"] = groups
        #template_data["criteria"][0]["compliance_summary"] = summary
        #template_data["criteria"][0]["tested"] = True

        dbh = DatabaseHandle(app)

        db = dbh.get_handle()
        db.connect()

        Criterion = dbh.get_model("Criterion")
        criterion = Criterion.get_by_id(1)

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

        groups = ec2.describe_security_groups(session, **params)

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
