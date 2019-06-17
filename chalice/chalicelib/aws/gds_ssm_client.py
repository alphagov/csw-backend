# GdsSsmClient
# extends GdsAwsClient
# implements aws sqs endpoint queries
import json
from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsSsmClient(GdsAwsClient):

    # get-queue-url
    # --queue-name < value >
    def get_parameter(self, parameter, decrypt):

        ssm = self.get_default_client("ssm")

        response = ssm.get_parameter(Name=parameter, WithDecryption=decrypt)
        param = response["Parameter"]

        return param

    def get_parameters(self, parameters, decrypt):

        ssm = self.get_default_client("ssm")

        response = ssm.get_parameters(Names=parameters, WithDecryption=decrypt)
        params = response["Parameters"]

        return params

    def get_parameters_by_path(self, path, decrypt, recursive=True):

        ssm = self.get_default_client("ssm")

        response = ssm.get_parameters_by_path(
            Path=path, Recursive=recursive, WithDecryption=decrypt
        )
        params = response["Parameters"]

        return params

    def parse_escaped_json_parameter(self, value):
        parsed = json.loads(value.replace("\\", ""))
        return parsed

    def get_parameter_value(self, params, name):

        value = None

        for item in params:

            if item["Name"] == name:
                value = item["Value"]

        return value
