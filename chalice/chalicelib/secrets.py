import boto3
import json


class Secrets:
    def get_secret_value(self, secret_name):

        self.client = boto3.client("secretsmanager")

        response = self.client.get_secret_value(SecretId=secret_name)

        return response["SecretString"]

    def parse_escaped_json_secret(self, value):
        parsed = json.loads(value.replace("\\", ""))
        return parsed
