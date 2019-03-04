"""
GdsCloudtrailClient
extends GdsAwsClient
implements AWS Cloudtrail endpoint queries
"""
from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsCloudtrailClient(GdsAwsClient):
    """
    """

    def describe_trails(self, session):
        """
        """
        cloudtrail_client = self.get_boto3_session_client('cloudtrail', session)
        data = cloudtrail_client.describe_trails().get('trailList', [])
        return data
