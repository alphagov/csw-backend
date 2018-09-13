# GdsEc2Client
# extends GdsAwsClient
# implements aws ec2 api queries
from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsEc2Client(GdsAwsClient):

    resource_type = "AWS::EC2::*"

    def describe_regions(self):

        ec2 = self.get_default_client('ec2')
        response = ec2.describe_regions()

        return response['Regions']
