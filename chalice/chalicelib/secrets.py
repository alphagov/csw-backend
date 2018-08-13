import boto3


class Secrets:

    client = boto3.client('secretsmanager')

    def get_secret_value(self, secret_name):

        response = self.client.get_secret_value(
            SecretId=secret_name
        )

        return response['SecretString']
