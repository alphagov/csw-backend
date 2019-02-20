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

    def describe_vpcs(self, region_name):

        ec2 = self.get_default_client('ec2', region=region_name)
        response = ec2.describe_vpcs()

        return response['Vpcs']

    def describe_flow_logs(self, vpc, region_name):

        ec2 = self.get_default_client('ec2', region=region_name)
        response = ec2.describe_flow_logs(Filters=[{'Name': 'resource-id', 'Values': [vpc['VpcId']]}])

        return response['FlowLogs']
