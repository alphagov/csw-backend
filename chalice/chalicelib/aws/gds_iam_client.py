# GdsIamClient
# extends GdsAwsClient
# implements aws ec2 api queries
from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsIamClient(GdsAwsClient):

    resource_type = "AWS::IAM::*"

    def list_users(self, session):

        iam = self.get_boto3_session_client("iam", session)
        response = iam.list_users()

        return response["Users"]

    def list_roles(self, session):

        iam = self.get_boto3_session_client("iam", session)
        response = iam.list_roles()

        return response["Roles"]

    def list_attached_role_policies(self, session, role_name):

        iam = self.get_boto3_session_client("iam", session)
        response = iam.list_attached_role_policies(RoleName=role_name)

        return response["AttachedPolicies"]

    def get_policy(self, session, policy_arn):
        iam = self.get_boto3_session_client("iam", session)
        response = iam.get_policy(PolicyArn=policy_arn)

        return response["Policy"]

    def get_policy_version(self, session, policy_arn, version):
        iam = self.get_boto3_session_client("iam", session)
        response = iam.get_policy_version(PolicyArn=policy_arn, VersionId=version)

        return response["PolicyVersion"]

    def get_policy_default_version(self, session, policy_arn):
        policy = self.get_policy(session, policy_arn)
        response = self.get_policy_version(session, policy_arn, policy["DefaultVersionId"])
        return response

    def get_role_policy(self, session, role_name, policy_name):

        iam = self.get_boto3_session_client("iam", session)
        response = iam.get_role_policy(RoleName=role_name, PolicyName=policy_name)

        return response

    def get_role(self, session, role_name):

        iam = self.get_boto3_session_client("iam", session)
        response = iam.get_role(RoleName=role_name)

        return response

    def list_role_tags(self, session, role_name):
        iam = self.get_boto3_session_client("iam", session)
        response = iam.list_role_tags(RoleName=role_name)

        return response["Tags"]

    def split_resource(self, resource):

        (type, name) = resource.split("/", 1)
        components = {
            "type": type,
            "name": name
        }

        return components

    def parse_arn_components(self, arn):

        components = super(GdsIamClient, self).parse_arn_components(arn)
        components["resource_components"] = self.split_resource(components["resource"])

        return components

    def get_remote_role(self, account_id, role_name):
        remote_session = self.get_chained_session(account_id)
        role = self.get_role(remote_session, role_name)
        return role["Role"]

    def get_role_trusted_arns(self, team_role):
        trust = team_role["AssumeRolePolicyDocument"]
        arns = []

        for statement in trust["Statement"]:
            if (
                    (statement["Effect"] == "Allow") and
                    ("AWS" in statement["Principal"])
            ):
                statement_arns = statement["Principal"]["AWS"]
                arns.extend(statement_arns)

        return arns

    def get_role_users(self, role):

        trusted_arns = self.get_role_trusted_arns(role)

        users = []
        for arn in trusted_arns:
            arn_components = self.parse_arn_components(arn)

            if arn_components["resource_components"]["type"] == "role":
                account_id = arn_components["account"]
                role_name = arn_components["resource_components"]["name"]
                remote_role = self.get_remote_role(account_id, role_name)
                remote_users = self.get_role_users(remote_role)
                users.extend(remote_users)

            elif arn_components["resource_components"]["type"] == "user":
                users.append(arn_components["resource_components"]["name"])

        # force uniqueness in case the same user belongs to multiple roles
        # or is identified as a user and as a role member
        user_set = set(users)
        unique_users = list(user_set)

        return unique_users

    def get_assumable_roles(self, policy_version):

        roles = []

        for statement in policy_version["Document"]["Statement"]:
            if (
                (statement["Effect"] == "Allow")  and
                (statement["Action"] == "sts:AssumeRole")
            ):
                roles.extend(statement["Resource"])

        return roles

    def get_role_accounts(self, roles):

        accounts = []
        for role_arn in roles:
            arn_components = self.parse_arn_components(role_arn)
            if arn_components["resource_components"]["name"] == self.chain["target_role"]:
                accounts.append(arn_components["account"])

        # force uniqueness in case the same user belongs to multiple roles
        # or is identified as a user and as a role member
        accounts_set = set(accounts)
        unique_accounts = list(accounts_set)
        return unique_accounts

