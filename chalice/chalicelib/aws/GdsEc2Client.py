# GdsEc2Client
# extends GdsAwsClient 
# implements aws ec2 api queries 
from aws.GdsAwsClient import GdsAwsClient

class GdsEc2Client(GdsAwsClient):
    
    def describe_security_groups(self, session, region='eu-west-2'):
    
        # get a boto3 client for the EC2 service in the given region (default to London)
        ec2 = self.get_boto3_session_client('ec2', session, region)

        # run describe security groups api call
        response = ec2.describe_security_groups()

        # return the security groups element of the response 
        security_groups = response['SecurityGroups']

        return security_groups