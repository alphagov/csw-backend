"""
GdsKmsClient
extends GdsAwsClient
implements aws Key Management Service endpoint queries
"""
from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsKmsClient(GdsAwsClient):
    """
    """

    def get_key_list_with_details(self, session):
        keys_list = self.get_key_list(session)
        for key in keys_list:
            key.update(self.get_key_rotation_status(session, key['KeyArn']))
            key.update({'KeyRotationEnabled': self.get_key_details(session, key['KeyArn']['KeyRotationEnabled'])})
        return keys_list

    def get_key_list(self, session):
        """
        """
        kms_client = self.get_boto3_session_client('kms', session)
        return kms_client.list_keys().get('Keys', [])

    def get_key_rotation_status(self, session, key_id_or_arn):
        """
        """
        kms_client = self.get_boto3_session_client('kms', session)
        return kms_client.get_key_rotation_status(KeyId=key_id_or_arn)['KeyRotationEnabled']

    def get_key_details(self, session, key_id_or_arn):
        """
        """
        kms_client = self.get_boto3_session_client('kms', session)
        return kms_client.describe_key(KeyId=key_id_or_arn).get('KeyMetadata', {})

    ###
    # methods for testing, not allowed by users' policies
    ###

    def create_key(self, session):
        """
        """
        kms_client = self.get_boto3_session_client('kms', session)
        return kms_client.create_key().get('KeyMetadata', {})

    def schedule_key_deletion(self, session, key_id_or_arn, days=7):
        """
        The number of days that the key can be deleted can be from 7 to 30, inlcusive.
        """
        kms_client = self.get_boto3_session_client('kms', session)
        return kms_client.schedule_key_deletion(
            KeyId=key_id_or_arn, PendingWindowInDays=days
        ).get('KeyMetadata', {})
