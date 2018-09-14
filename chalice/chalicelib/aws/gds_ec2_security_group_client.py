# GdsEc2Client
# extends GdsAwsClient
# implements aws ec2 api queries
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
