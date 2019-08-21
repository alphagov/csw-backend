# GdsS3Client
# extends GdsAwsClient
# implements aws s3 and s3api endpoint queries

from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsS3Client(GdsAwsClient):

    # list buckets
    def get_bucket_list(self, session):

        s3 = self.get_boto3_session_client("s3", session)
        response = s3.list_buckets()
        buckets = response["Buckets"]

        return buckets

    def get_bucket_policy(self, session, bucket_name):

        try:
            s3 = self.get_boto3_session_client("s3", session)
            response = s3.get_bucket_policy(Bucket=bucket_name)
            # This is actually a JSON string instead of a dict. Don't ask me why
            policy = response["Policy"]
        except Exception as exception:
            # This is a debug log since buckets don't have to have policies
            self.app.log.debug(self.app.utilities.get_typed_exception())
            policy = "{}"

        return policy

    def get_bucket_versioning(self, session, bucket_name):
        s3 = self.get_boto3_session_client("s3", session)
        # If the trusted advisor check result has not been recently refreshed
        # you can get a list of buckets including buckets that no longer exist.
        # This try catch traps the exception if you try to call get_bucket_versioning
        # for a bucket that doesn't exist.
        versioning = None
        try:
            self.app.log.debug(f"Get bucket versioning for ({bucket_name})")
            # Don't try to get versioning without a name
            if bucket_name:
                versioning = s3.get_bucket_versioning(Bucket=bucket_name)
        except Exception:
            self.app.log.debug(self.app.utilities.get_typed_exception())

        return versioning

    def get_bucket_encryption(self, session, bucket_name):

        s3 = self.get_boto3_session_client("s3", session)
        encryption = None
        try:
            self.app.log.debug(f"Getting encryption data for {bucket_name}")
            encryption = s3.get_bucket_encryption(Bucket=bucket_name)
        except Exception:
            self.app.log.debug(self.app.utilities.get_typed_exception())

        return encryption

    def get_bucket_acl(self, session, bucket_name):

        s3 = self.get_boto3_session_client("s3", session)
        acl = None
        try:
            self.app.log.debug(f"Getting ACL for {bucket_name}")
            acl = s3.get_bucket_acl(Bucket=bucket_name)
        except Exception:
            self.app.log.error(self.app.utilities.get_typed_exception())

        return acl
