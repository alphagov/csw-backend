# AwsIamValidateInspectorPolicy
# extends GdsIamClient
# implements aws ec2 api queries
import urllib.request
from chalicelib.aws.gds_iam_client import GdsIamClient


class AwsIamValidateInspectorPolicy(GdsIamClient):

    policy_url = "https://raw.githubusercontent.com/alphagov/csw-client-role/master/csw_role/json/policy.json"

    resource_type = "AWS::IAM::Policy"

    role_name_default = "_CstSecurityInspectorRole"

    def get_inspector_role_policy_data(self, session):

        role_name = self.app.prefix + self.role_name_default

        policy_name = role_name + "Policy"

        data = self.get_role_policy(self, role_name, policy_name)

        policy = self.get_current_policy_version(session)

        data['PolicyRequired'] = policy

        self.app.log.debug("AppliedPolicy: " + data['PolicyDocument'])

        return [data]

    def evaluate(self, event, item, whitelist=[]):

        # TODO ensure both docs end up in the same format JSON (pretty) or dict
        # -- and in th same order
        # compare item['PolicyRequired'] to item['PolicyDocument']

    def get_current_policy_version(self, session):

        caller = self.get_caller_details(session)
        account = caller['Account']

        current_policy_default = urllib.request.urlopen("http://example.com/foo/bar").read()

        # replace the policy placeholders to populate Resource ARN restrictions
        current_policy_account = current_policy_default.replace('${account_id}', account)
        current_policy_account = current_policy_account.replace('${prefix}', self.app.prefix)

        self.app.log.debug("DefaultPolicy: " + current_policy_account)

        return current_policy_account
