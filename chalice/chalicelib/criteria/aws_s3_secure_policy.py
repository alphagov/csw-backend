# AwsS3SecurePolicy
# extends CriteriaDefault
# Checks if there is a policy in each bucket in the target account
from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_s3_client import GdsS3Client


class AwsS3SecurePolicy(CriteriaDefault):

    active = True

    ClientClass = GdsS3Client

    resource_type = ""

    is_regional = False

    title = "S3 - Insecure Bucket Policies"

    description = "Checks whether the S3 bucket has a policy that only allows connection via HTTPS"

    why_is_it_important = ("HTTPS allows for data transferred to and from S3 buckets to be encrypted. If this data is "
                           "not encrypted, it would allow for sensitive data to be intercepted in transit.")

    how_do_i_fix_it = "Attach a policy with a condition that only allows access through HTTPS."

    def __init__(self, app):
        super(AwsS3SecurePolicy, self).__init__(app)

    def get_data(self, session, **kwargs):
        self.app.log.debug("Getting a list of buckets in this account")
        buckets = self.client.get_bucket_list(session)
        self.app.log.debug("Adding a 'Policy' key to these buckets")
        for bucket in buckets:
            # I know mutating what you're iterating over is a bad idea...
            bucket['Policy'] = self.client.get_bucket_policy(session, bucket['Name'])

        return buckets

    def translate(self, data):

        item = {
            "resource_id": 'arn:aws:s3:::' + data.get('Name', ''),
            "resource_name": data.get('Name', '')
        }

        return item

    def evaluate(self, event, role, whitelist=[]):
        compliance_type = ""
        evaluation = self.build_evaluation(
            "root",
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )

        return evaluation
