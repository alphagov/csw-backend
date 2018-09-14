# GdsEc2Client
# extends GdsAwsClient
# implements aws ec2 api queries
from chalicelib.aws.gds_ec2_client import GdsEc2Client


class GdsEc2SecurityGroupClient(GdsEc2Client):

    resource_type = "AWS::EC2::SecurityGroup"

    def describe_security_groups(self, session, **kwargs):

        # get a boto3 client for the EC2 service in the given region (default to London)
        ec2 = self.get_boto3_session_client('ec2', session, kwargs["region"])

        #if hasattr(self,'app'):
        #    self.app.log.debug('got session client')

        # run describe security groups api call
        response = ec2.describe_security_groups()

        #if hasattr(self, 'app'):
        #    self.app.log.debug('got response: ' + str(response))

        # return the security groups element of the response
        security_groups = response['SecurityGroups']

        return security_groups

    def translate(self, data):

        item = {
            "resource_id": data['GroupId'],
            "resource_name": data['GroupName'],
        }

        return item
