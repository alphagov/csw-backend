# AwsIamRolesWithTrustRelationship
# extends GdsIamClient
# Checks if there is at least one role which defines a trust relationship that contains IAM users
# from a separate "main account".
import json
import re
from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_iam_client import GdsIamClient


class AwsIamRolesWithTrustRelationship(CriteriaDefault):

    active = True

    ClientClass = GdsIamClient

    resource_type = "AWS::IAM::Role"

    title = "Cloud Security Watch - IAM used correctly"

    description = ("Checks whether there is at least one role within the account that has a trust relationship"
                   "with an IAM user from a different account.")

    why_is_it_important = ("Delivery accounts are set up such that there need not be any IAM users in them, "
                           "with users assuming a role into the delivery account instead.<br />"
                           "If there is no role defined in the account which doesn't trust an IAM user from a "
                           "different account, there is no way to gain access to the delivery account without logging "
                           "in as the root user, which is not recommended.")

    how_do_i_fix_it = ("Create a role that trusts an IAM user from a separate account, to allow them to assume a "
                       "role into your account.")

    # It would be nice to define a default here that contains the GDS account number (so we can use
    # it to construct a regex to check the trust relationship), but we probably don't want to commit
    # that to a public repo. Check the environment variables to see if the GDS account number is
    # defined there. If not, we probably want to define it at some point in the setup
    # try:
    #   user_account = os.environ["IAM_USER_ACCOUNT"]
    # except Exception:
    #   user_account = ""

    def __init__(self, app):
        super(AwsIamRolesWithTrustRelationship, self).__init__(app)
        self.user_account = self.retrieve_user_account()
        self.iam_user_regex = re.compile(self.user_account + ":user")

    def retrieve_user_account(self):
        return "010101010101"  # TODO: dummy value defined in the unit test - change for final

    def get_data(self, session, **kwargs):
        self.app.log.debug("Getting a list of roles in the account...")

        return self.client.list_roles(session)

    def translate(self, data):

        item = {
            "resource_id": data.get('Arn', ''),
            "resource_name": data.get('RoleName', '')
        }

        return item

    def evaluate(self, event, role, whitelist=[]):

        compliance_type = ""

        self.app.log.debug(f"Evaluating role with name {role['RoleName']} and ARN {role['Arn']}")

        principal = role["AssumeRolePolicyDocument"]["Statement"][0]["Principal"]

        self.app.log.debug(f"Principal of that role: {json.dumps(principal)}")

        if "AWS" in principal:
            # If value of the AWS key isn't a list, it's a str, so put it in a list to iterate over it correctly
            for arn in (principal["AWS"] if isinstance(principal["AWS"], list) else [principal["AWS"]]):
                if self.iam_user_regex.search(arn):  # matches the iam_user format we're looking for
                    compliance_type = "COMPLIANT"
                    self.app.log.debug(f"Role: {role['RoleName']} is found to be compliant")
                    break  # don't need to loop over the rest, we've got an IAM user matched
            else:  # We didn't break out of the loop, no arns have been matched
                compliance_type = "NON_COMPLIANT"
                self.app.log.debug("Role does not trust any IAM users from the main account")
                self.annotation = ("<p>No trusted users: This role does not define any IAM users from the account "
                                   f"{self.user_account} in their trust relationship.</p>"
                                   "<p>This prevents any users from the trusted account assuming this role. "
                                   "(However, it does not prevent IAM users from other accounts from "
                                   "assuming this role.)</p>")
        else:
            compliance_type = "NON_COMPLIANT"
            self.app.log.debug("Principal does not define any AWS identites")
            self.annotation = ("<p>Invalid service: This role trusts a service, such as EC2 or Lambda, "
                               "instead of an identity.</p>"
                               "<p>This role is not designed for any user (from any account) to assume it.</p>")

        evaluation = self.build_evaluation(
            "root",
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )

        return evaluation
