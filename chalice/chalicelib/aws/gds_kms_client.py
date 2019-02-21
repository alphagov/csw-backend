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
            key.update(self.get_key_details(session, key['KeyArn']))
        self.app.log.debug('KMS::get_key_list_with_details')
        self.app.log.debug(type(keys_list))
        self.app.log.debug(keys_list)
        return keys_list

    def get_key_list(self, session):
        """
        """
        kms_client = self.get_boto3_session_client('kms', session)
        data = kms_client.list_keys().get('Keys', [])
        self.app.log.debug('KMS::get_key_list')
        self.app.log.debug(type(data))
        self.app.log.debug(data)
        return data

    def get_key_rotation_status(self, session, key_id_or_arn):
        """
        """
        kms_client = self.get_boto3_session_client('kms', session)
        data = kms_client.get_key_rotation_status(KeyId=key_id_or_arn)
        self.app.log.debug('KMS::get_key_rotation_status')
        self.app.log.debug(type(data))
        self.app.log.debug(data)
        return data

    def get_key_details(self, session, key_id_or_arn):
        """
        """
        kms_client = self.get_boto3_session_client('kms', session)
        data = kms_client.describe_key(KeyId=key_id_or_arn)
        self.app.log.debug('KMS::get_key_details')
        self.app.log.debug(type(data))
        self.app.log.debug(data)
        return data['KeyMetadata']

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
