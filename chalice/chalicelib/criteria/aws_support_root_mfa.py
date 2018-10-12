# AwsSupportRootMfa
# extends GdsSupportClient
# implements aws ec2 api queries
from chalicelib.aws.gds_support_client import GdsSupportClient


class AwsSupportRootMfa(GdsSupportClient):

    resource_type = "AWS::IAM::User"
    check_id = "7DAFEmoDos"
    language = "en"
    region = "us-east-1"

    def get_root_mfa_status_data(self, session):

        output = self.describe_trusted_advisor_check_result(
            session,
            checkId=self.check_id,
            language=self.language,
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