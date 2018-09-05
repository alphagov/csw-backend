# GdsS3Client
# extends GdsAwsClient
# implements aws s3 and s3api endpoint queries

from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsSecretsManagerClient(GdsAwsClient):

    def get_secret_value(self, secret_name):

        secrets = self.get_boto3_client('secretsmanager')

        response = secrets.get_secret_value(
            SecretId=secret_name
        )

        return response['SecretString']
