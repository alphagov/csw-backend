# AwsIamRolesWithTrustRelationship
# extends GdsIamClient
# Checks if there is at least one role which defines a trust relationship that contains IAM users
# from a separate "main account".
import json
import os
import re
from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_iam_client import GdsIamClient



class AwsIamRolesWithTrustRelationship(CriteriaDefault):

    active = True

    ClientClass = GdsIamClient

    resource_type = "AWS::IAM::Role"

    title = "Cloud Security Watch - IAM used correctly"

    description = """Checks whether there is at least one role within the account that has a trust relationship
        with an IAM user from a different account."""

    why_is_it_important = """Delivery accounts are set up such that there need not be any new IAM users in them,
        with users assuming a role into the delivery account instead. If there is no role defined in the account
        which doesn't refer to an IAM user from a different account, there is no way to gain access to the
        delivery account without logging in as the root user, which is not recommended."""

    how_do_i_fix_it = """Create a role that trusts an IAM user from a separate account, to allow them to assume a
        role into your account."""

    # It would be nice to define a default here that contains the GDS account number (so we can use
    # it to construct a regex to check the trust relationship), but we probably don't want to commit
    # that to a public repo. Check the environment variables to see if the GDS account number is
    # defined there. If not, we probably want to define it at some point in the setup
    #try:
        #user_account = os.environ["IAM_USER_ACCOUNT"]
    #except Exception:
        #user_account = ""
    user_account = "010101010101" # dummy value defined in the unit test

    iam_user_regex = re.compile(user_account + ":user")


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
            for arn in principal["AWS"]:
                if self.iam_user_regex.search(arn): # matches the iam_user format we look for
                    compliance_type = "COMPLIANT"
                    self.app.log.debug(f"Role: {role['RoleName']} is found to be compliant")
                    break # don't need to loop over the rest, we've got an IAM user matched

        if not compliance_type:
            compliance_type = "NON_COMPLIANT"
            self.app.log.debug("No roles are compliant")
            self.annotation = ("<p>There are no roles in the account that define an IAM user from "
                               f"the account {self.user_account} in their trust relationship.</p>")
            self.annotation += ("<p>Users cannot assume role into your account. Make sure that you "
                                "have a role that defines an appropriate trust relationship.</p>")

        evaluation = self.build_evaluation(
            "root",
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )

        return evaluation
