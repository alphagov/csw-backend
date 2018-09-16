# GdsEc2Client
# extends GdsAwsClient
# implements aws ec2 api queries
import re
from netaddr import IPNetwork
from chalicelib.aws.gds_ec2_client import GdsEc2Client


class GdsEc2SecurityGroupClient(GdsEc2Client):

    resource_type = "AWS::EC2::SecurityGroup"

    def describe_security_groups(self, session, **kwargs):

        # get a boto3 client for the EC2 service in the given region (default to London)
        ec2 = self.get_boto3_session_client('ec2', session, kwargs["region"])

        # run describe security groups api call
        response = ec2.describe_security_groups()

        # return the security groups element of the response
        security_groups = response['SecurityGroups']

        return security_groups

    def translate(self, data):

        item = {
            "resource_id": data['GroupId'],
            "resource_name": data['GroupName'],
        }

        return item

    def is_protocol(self, rule, required_protocol):

        protocol = rule['IpProtocol']

        self.app.log.debug('protocol: ' + protocol)

        return protocol in [required_protocol, '-1']

    def get_port_range(self, rule):

        range = []
        if "FromPort" in rule:
            range.append(str(rule["FromPort"]))

        if "ToPort" in rule:
            range.append(str(rule["ToPort"]))

        # if port range from and to are the same just return one
        if len(range) == 2 and range[0] == range[1]:
            port_range = range[0]
        else:
            port_range = '-'.join(range)

        return port_range

    def in_port_range(self, rule, required_port):

        if ('FromPort' in rule):
            from_port = rule['FromPort']
            to_port = rule['ToPort']
            in_range = ((from_port <= required_port) and (to_port >= required_port))
        else:
            in_range = False

        return in_range

    def parse_v4_cidr(self, cidr):

        cidr_pattern = '^(\d+)\.(\d+)\.(\d+)\.(\d+)\/(\d+)$'

        m = re.search(cidr_pattern, cidr)

        parsed = {
            "cidr": m.group(0),
            "a": int(m.group(1)),
            "b": int(m.group(2)),
            "c": int(m.group(3)),
            "d": int(m.group(4)),
            "mask": int(m.group(5)),
            "v": 4
        }
        return parsed

    def parse_v6_cidr(self, cidr):

        cidr_pattern = '^([0-9a-f]*)\:([0-9a-f]*)\:([0-9a-f]*)\/(\d+)$'

        m = re.search(cidr_pattern, cidr)

        parsed = {
            "cidr": m.group(0),
            "a": int(m.group(1)),
            "b": int(m.group(2)),
            "c": int(m.group(3)),
            "mask": int(m.group(4)),
            "v": 6
        }
        return parsed

    def cidr_is_private_network(self, cidr):

        parsed_cidr = self.parse_v4_cidr(cidr)

        is_private = False
        if parsed_cidr.a == 10:
            is_private = True
        elif parsed_cidr.a == 192 and parsed_cidr.b == 168:
            is_private = True
        elif parsed_cidr.a == 172 and (16 <= parsed_cidr.b <= 31):
            is_private = True

        return is_private

    def parent_cidr_contains_chlid_cidr(self, parent, child):

        return IPNetwork(child) in IPNetwork(parent)

    def cidrs_equivalent(self, cidr_a, cidr_b):

        a_in_b = self.parent_cidr_contains_chlid_cidr(self, cidr_a, cidr_b)
        b_in_a = self.parent_cidr_contains_chlid_cidr(self, cidr_b, cidr_a)

        return (a_in_b and b_in_a)
