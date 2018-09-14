
def execute_test_ports_ingress_ssh(app, load_route_services):

    try:
        load_route_services()

        Client = app.utilities.get_class_by_name(
            "chalicelib.criteria.aws_ec2_security_group_ingress_ssh.AwsEc2SecurityGroupIngressSsh"
        )
        ec2 = Client(app)

        session = ec2.get_session(account='103495720024', role='csw-dan_CstSecurityInspectorRole')

        groups = ec2.describe_security_groups(session, **{"region": 'eu-west-1'})

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
        response = { "body": str(err) }

    return response


def execute_test_ports_ingress_open(app, load_route_services):


    try:
        load_route_services()

        Client = app.utilities.get_class_by_name(
            "chalicelib.criteria.aws_ec2_security_group_ingress_open.AwsEc2SecurityGroupIngressOpen"
        )
        ec2 = Client(app)

        session = ec2.get_session(account='103495720024', role='csw-dan_CstSecurityInspectorRole')

        groups = ec2.describe_security_groups(session, **{ "region": 'eu-west-1'})

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
        response = { "body": str(err) }

    return response
