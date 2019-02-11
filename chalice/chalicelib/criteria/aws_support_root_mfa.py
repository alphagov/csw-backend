# AwsSupportRootMfa
# extends GdsSupportClient
# implements aws ec2 api queries
from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_support_client import GdsSupportClient


class AwsSupportRootMfa(CriteriaDefault):

    active = True

    resource_type = "AWS::IAM::User"
    check_id = "7DAFEmoDos"
    language = "en"
    region = "us-east-1"

    ClientClass = GdsSupportClient

    title = "MFA: Muti-factor authentication is enabled for the root account"

    description = """Checks the root account and warns if multi-factor authentication (MFA) 
    is not enabled. For increased security, we recommend that you protect your account by 
    using MFA, which requires a user to enter a unique authentication code from their MFA 
    hardware or virtual device when interacting with the AWS console and associated websites."""

    why_is_it_important = """MFA on root is not enabled. If the account gets compromised, 
    an attacker will be able to access all resources in the root account, deleting configuration, 
    creating resources for malicious activity or to lunch further attacks."""

    how_do_i_fix_it = """If you have the root credentials for your account enable MFA - otherwise 
    speak to Tech-ops Reliability Engineering 
    <a target="slack" href="https://gds.slack.com/messages/reliability-eng/">#reliability-engineering</a>"""

    def get_data(self, session, **kwargs):

        output = self.client.describe_trusted_advisor_check_result(
            session,
            checkId=self.check_id,
            language=self.language
        )

        self.app.log.debug(self.app.utilities.to_json(output))

        # Return as a list of 1 item for consistency with other checks
        return [output]

    def translate(self, data):

        item = {
            "resource_id": "root",
            "resource_name": "Root Account",
        }

        return item

    def evaluate(self, event, item, whitelist=[]):

        if item['status'] == 'ok':
            compliance_type = "COMPLIANT"
        else:
            compliance_type = "NON_COMPLIANT"

        evaluation = self.build_evaluation(
            "root",
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )

        return evaluation