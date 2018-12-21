# GdsIamClient
# extends GdsAwsClient
# implements aws ec2 api queries
from chalicelib.aws.gds_aws_client import GdsAwsClient

class GdsIamClient(GdsAwsClient):

    resource_type = "AWS::IAM::*"

    def list_users(self, session):

        iam = self.get_boto3_session_client('iam', session)
        response = iam.list_users()

        return response['Users']

    def list_roles(self, session):

        iam = self.get_boto3_session_client('iam', session)
        response = iam.list_roles()

        return response['Roles']

    def get_role_policy(self, session, role_name, policy_name):

        iam = self.get_boto3_session_client('iam', session)
        response = iam.get_role_policy(
            RoleName=role_name,
            PolicyName=policy_name
        )

        return response