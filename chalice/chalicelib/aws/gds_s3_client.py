# GdsS3Client
# extends GdsAwsClient
# implements aws s3 and s3api endpoint queries

from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsS3Client(GdsAwsClient):

    # list buckets
    def get_bucket_list(self, session):

        s3 = self.get_boto3_session_client('s3', session)
        response = s3.list_buckets()
        buckets = response['Buckets']

        return buckets

    def get_bucket_policy(self, session, bucket_name):

        try:
            s3 = self.get_boto3_session_client('s3', session)
            response = s3.get_bucket_policy(
                Bucket=bucket_name
            )
            policy = response['Policy']  # This is actually a JSON string instead of a dict. Don't ask me why
        except Exception as exception:
            policy = str(exception)

        return policy

    def get_bucket_versioning(self, session, bucket_name):

        s3 = self.get_boto3_session_client('s3', session)
        try:
            versioning = s3.get_bucket_versioning(Bucket=bucket_name)
        except Exception as e:  # Usually a botocore.exceptions.ClientError - Access Denied
            versioning = {"csw_access_denied_error": str(e)}

        return versioning
