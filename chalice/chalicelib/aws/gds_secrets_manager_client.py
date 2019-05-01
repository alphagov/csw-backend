# GdsS3Client
# extends GdsAwsClient
# implements aws secrets manager endpoint queries
import json
from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsSecretsManagerClient(GdsAwsClient):
    def get_secret_value(self, secret_name):

        secrets = self.get_default_client("secretsmanager")

        response = secrets.get_secret_value(SecretId=secret_name)

        return response["SecretString"]

    def parse_escaped_json_secret(self, value):
        parsed = json.loads(value.replace("\\", ""))
        return parsed
