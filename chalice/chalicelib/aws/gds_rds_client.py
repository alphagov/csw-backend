"""
GdsRdsClient
extends GdsAwsClient
implements aws Key Management Service endpoint queries
"""
from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsRdsClient(GdsAwsClient):
    """
    """

    def describe_db_instances(self, session):
        """
        """
        kms_client = self.get_boto3_session_client('rds', session)
        data = kms_client.describe_db_instances().get('DBInstances', [])
        self.app.log.debug('RDS::describe_db_instances')
        self.app.log.debug(type(data))
        self.app.log.debug(data)
        return data
