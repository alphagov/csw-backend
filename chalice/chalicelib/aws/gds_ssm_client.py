# GdsSsmClient
# extends GdsAwsClient
# implements aws sqs endpoint queries
import json
from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsSsmClient(GdsAwsClient):

    # get-queue-url
    # --queue-name < value >
    def get_parameter(self, session, parameter, decrypt):

        ssm = self.get_boto3_session_client('ssm', session)
        
        response = ssm.get_parameter(
            Name=parameter,
            WithDecryption=decrypt
        )
        param = response['Parameter']

        return param

    def get_parameters(self, session, parameters, decrypt): 

        ssm = self.get_boto3_session_client('ssm', session)
        
        response = ssm.get_parameters(
            Name=parameters,
            WithDecryption=decrypt
        )
        params = response['Parameters']

        return params

    def parse_escaped_json_parameter(self, value):
        parsed = json.loads(value.replace('\\', ''))
        return parsed

    def get_parameter_value(self, params, name): 

        value = None

        for item in params:

            if item.Name == name: 
                value = item.value

        return value