"""
"""
from chalicelib.aws.gds_ec2_security_group_client import GdsEc2SecurityGroupClient
from chalicelib.criteria.criteria_default import CriteriaDefault


class UnrestrictedEgressSecurityGroups(CriteriaDefault):
    """
    """
    active = True

    def __init__(self, app):
        self.ClientClass = GdsEc2SecurityGroupClient
        self.resource_type = 'AWS::EC2::SecurityGroup'
        self.annotation = ''
        self.is_regional = True
        self.title = 'Unrestricted Egress Security Groups'
        self.description = (
            'Checks security groups for rules that allow unrestricted access to a resource.'
        )
        self.why_is_it_important = (
            'Unrestricted access increases opportunities for malicious activity '
            '(hacking, denial-of-service attacks, loss of data).'
        )
        self.how_do_i_fix_it = (
            'Restrict access to only those IP addresses that require it. <br />'
            'To restrict access to a specific IP address, set the suffix to /32 ''(for example, 192.0.2.10/32). <br />'
            'Be sure to delete overly permissive rules after creating rules that are more restrictive <br />. '
            'Additional Resources:<br />.'
            '<a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-network-security.html">'
            'Amazon EC2 Security Groups</a><br />.'
            '<a href="https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing">'
            'Classless Inter-Domain Routing</a> (Wikipedia)<br />.'
        )
        super(UnrestrictedEgressSecurityGroups, self).__init__(app)

    def get_data(self, session, **kwargs):
        return self.client.describe_security_groups(session, **kwargs)

    def translate(self, data):
        print(data, type(data))
        return {
            "resource_id": data['GroupId'],
            "resource_name": data['GroupName'],
        }

    def evaluate(self, event, item, whitelist=[]):
        """
        """
        compliance_type = 'COMPLIANT'
        for egress_permission in item['IpPermissionsEgress']:
            if egress_permission['IpProtocol'] == '-1':
                for ip_range in egress_permission['IpRanges']:
                    if ip_range['CidrIp'] == '0.0.0.0/0':
                        compliance_type = 'NON_COMPLIANT'
                        self.annotation = 'This security group has unrestricted outbound traffic.'
        return self.build_evaluation(
            item['GroupId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )
