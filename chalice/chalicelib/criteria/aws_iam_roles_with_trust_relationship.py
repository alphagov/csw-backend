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

    is_regional = False

    title = "IAM Roles: At least one role trusts IAM users from an authorised authentication AWS account"

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
        self.iam_user_regex = re.compile(r"arn:aws:iam::(\d{12}):user/.+")

    def retrieve_user_account(self):
        return "622626885786"  # TODO: Find a better way to retrieve the trusted account number

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
            identities = (principal["AWS"] if isinstance(principal["AWS"], list) else [principal["AWS"]])
            users = [self.iam_user_regex.fullmatch(arn) for arn in identities]
            if set(users) == {None}:  # No matches
                compliance_type = "NON_COMPLIANT"
                self.annotation = ("<p>No trusted users: This role does not define any IAM users.</p>"
                                   "<p>This prevents any users from assuming this role. (However, it does not prevent "
                                   "IAM users from other accounts from assuming this role.)</p>")
            else:
                for user_match in users:
                    if user_match and user_match.group(1) != self.user_account:
                        compliance_type = "NON_COMPLIANT"
                        self.app.log.debug("Role has an IAM User from unknown AWS account defined in its trust policy")
                        self.annotation = ("<p>Untrusted user: This role trusts an IAM user from an AWS account that "
                                           "is not recognised. Roles may only trust IAM Users from account number "
                                           f"{self.user_account}.</p>"
                                           "<p>This is a security risk, as it allows an IAM User from an unkown "
                                           "account to assume a role into this account, with potentially significant "
                                           "privileges.</p>")
                        break  # don't need to loop over the rest, we've got an IAM user matched
                else:   # There must be at least 1 User from the self.user_account, with none that match other accounts
                    compliance_type = "COMPLIANT"
                    self.app.log.debug(f"Role: {role['RoleName']} is found to be compliant")

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
