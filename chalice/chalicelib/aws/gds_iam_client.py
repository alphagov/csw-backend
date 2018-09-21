# GdsIamClient
# extends GdsAwsClient
# implements aws ec2 api queries
from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsIamClient(GdsAwsClient):

    resource_type = "AWS::IAM::*"

    def list_users(self):

        iam = self.get_default_client('iam')
        response = iam.list_users()

        return response['Users']

    def list_roles(self):

        iam = self.get_default_client('iam')
        response = iam.list_users()

        return response['Roles']

    def get_role_policy(self, role_name, policy_name):

        iam = self.get_default_client('iam')
        response = iam.get_role_policy(
            RoleName=role_name,
            PolicyName=policy_name
        )

        return response