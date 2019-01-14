# GdsIamClient
# extends GdsAwsClient
# implements aws ec2 api queries
from chalicelib.aws.gds_aws_client import GdsAwsClient

class GdsIamClient(GdsAwsClient):

    resource_type = "AWS::IAM::*"

    def __init__(self):
        self.iam = self.get_boto3_session_client('iam', session) 

    def list_users(self, session):

        response = self.iam.list_users()

        return response['Users']

    def list_roles(self, session):

        response = self.iam.list_roles()

        return response['Roles']

    def get_role_policy(self, session, role_name, policy_name):

        response = self.iam.get_role_policy(
            RoleName=role_name,
            PolicyName=policy_name
        )

        return response