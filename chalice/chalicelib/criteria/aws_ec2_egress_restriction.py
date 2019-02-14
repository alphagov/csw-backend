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
        self.title = 'EC2 Security Groups: Egress traffic is restricted by port or CIDR'
        self.description = (
            'Checks security groups for egress rules that allow unrestricted access to a resource.'
        )
        self.why_is_it_important = (
            'Unrestricted outbound network traffic increases opportunities for malicious activity '
            '(hacking, denial-of-service attacks, loss of data). <br />'
            'If internal servers are compromised, they can pose a threat to a larger network of resources, '
            'for example especially when attempting to steal sensitive data '
            'or communicate with command and control systems.'
        )
        self.how_do_i_fix_it = (
            'Restrict outbound network traffic to only those IP addresses and ports that require it. '
            '<a href="https://aws.amazon.com/answers/networking/controlling-vpc-egress-traffic/">'
            'Additional Resources</a>.'
        )
        super(UnrestrictedEgressSecurityGroups, self).__init__(app)

    def get_data(self, session, **kwargs):
        return self.client.describe_security_groups(session, **kwargs)

    def translate(self, data):
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
