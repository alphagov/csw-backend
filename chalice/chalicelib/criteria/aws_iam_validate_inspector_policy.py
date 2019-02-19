# AwsIamValidateInspectorPolicy
# extends GdsIamClient
# implements aws ec2 api queries
import requests
import json
from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_iam_client import GdsIamClient



class AwsIamValidateInspectorPolicy(CriteriaDefault):

    active = True

    ClientClass = GdsIamClient

    resource_type = "AWS::IAM::Policy"

    title = "IAM Roles: The inspector role policy for Cloud Security Watch is up to date"

    description = (
        'Checks that the IAM Inspector role policy used by this service has been updated to the current version and '
        'has not been altered.'
    )

    why_is_it_important = """If the role policy does not grant the right permissions checks will fail 
        to be processed."""

    how_do_i_fix_it = """Update the module and re-run the terraform apply to re-deploy the role and policy."""

    policy_url = "https://raw.githubusercontent.com/alphagov/csw-client-role/master/csw_role/json/policy.json"

    role_name_default = "_CstSecurityInspectorRole"

    def get_data(self, session, **kwargs):

        role_name = self.app.prefix + self.role_name_default

        self.app.log.debug("Role: " + role_name)

        policy_name = role_name + "Policy"

        self.app.log.debug("Policy: " + policy_name)

        data = self.client.get_role_policy(session, role_name, policy_name)

        applied_policy_json = json.dumps(data['PolicyDocument'])

        self.app.log.debug("Policy document: " + applied_policy_json)

        self.app.log.debug("Get github current version")

        standard_policy = self.get_current_policy_version(session)
        standard_policy_json = json.dumps(standard_policy)

        self.app.log.debug("Current version: " + standard_policy_json)

        self.app.log.debug("Policies equal = " + str(applied_policy_json == standard_policy_json))

        data['PolicyUrl'] = self.policy_url
        data['PolicyRequired'] = standard_policy

        return [data]

    def translate(self, data):

        item = {
            "resource_id": data['RoleName'],
            "resource_name": data['RoleName'],
        }

        return item

    def evaluate(self, event, item, whitelist=[]):

        # TODO ensure both docs end up in the same format JSON (pretty) or dict
        # -- and in th same order
        # compare item['PolicyRequired'] to item['PolicyDocument']

        applied = json.dumps(item['PolicyDocument'])
        required = json.dumps(item['PolicyRequired'])
        if applied == required:
            compliance_type = "COMPLIANT"
        else:
            compliance_type = "NON_COMPLIANT"
            role_name = item['RoleName']
            self.annotation = f"<p>The policy attached to {role_name} does not match the current version.</p>"
            self.annotation += f"<p>The current policy can be viewed on <a target=\"github\" href=\"{self.policy_url}\">GitHub</a>.</p>"
            self.annotation += "<p>You may need to run Terraform again.</p>"

        evaluation = self.build_evaluation(
            "root",
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )

        return evaluation

    def get_current_policy_version(self, session):

        current_policy = None
        try:
            caller = self.client.get_caller_details(session)

            self.app.log.debug(json.dumps(caller))

            account = caller['Account']

            self.app.log.debug("Account: " + account)

            self.app.log.debug("Raw policy url: " + self.policy_url)

            r = requests.request('GET', self.policy_url)

            self.app.log.debug("GitHub status code: " + str(r.status_code))

            current_policy_default = r.text

            self.app.log.debug("GitHub current: " + current_policy_default)

            # replace the policy placeholders to populate Resource ARN restrictions
            current_policy_account = current_policy_default.replace('${account_id}', account)
            current_policy_account = current_policy_account.replace('${prefix}', self.app.prefix)

            # parse and encode to standardise formatting.
            current_policy = json.loads(current_policy_account)

            self.app.log.debug("DefaultPolicy: " + current_policy_account)

        except Exception as err:

            self.app.log.error("Failed to get current policy: " + str(err))

        return current_policy
