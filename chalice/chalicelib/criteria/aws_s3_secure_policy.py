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

    def evaluate(self, event, bucket, whitelist=[]):
        compliance_type = ""
        self.app.log.debug(f"Evaluating bucket with name {bucket['Name']}")
        if not isinstance(bucket['Policy'], dict):  # Failure: no policy
            log_string = "Bucket does not have a policy"
            compliance_type = "NOT_COMPLIANT"
            self.annotation = ("<p>This bucket has no policy attached.<p>"
                               "<p>This means you cannot prevent non-HTTPS connections to your bucket, which poses a "
                               "security risk.</p>")
        else:
            for statement in bucket['Policy']['Statement']:
                if 'Condition' not in statement:  # Failure: No condition
                    log_string = "Bucket does not have any conditions on its policy"
                    compliance_type = "NOT_COMPLIANT"
                    self.annotation = ("<p>This bucket's policy does not have a condition.</p>"
                                       "<p>This means you cannot prevent non-HTTPS connections to your bucket, "
                                       "which poses a security risk.</p>")
                    break
                else:
                    secure = statement['Condition'].get('Bool', {}).get('aws:SecureTransport')
                    if secure == "false":  # secure is either "true", "false", or None if it didn't exist
                        # Failure: HTTPS is specifically disallowed
                        log_string = "Bucket's policy condition explicitly disallows HTTPS"
                        compliance_type = "NOT_COMPLIANT"
                        self.annotation = ("<p>This bucket's policy explicitly disallows HTTPS.</p>"
                                           "<p>This means you cannot have any HTTPS connections to your bucket, "
                                           "which poses a security risk.</p>")
                        break
                    if not secure:  # testing if secure is None
                        # Failure: no secure transport condition
                        log_string = "Bucket does not disallow insecure connections"
                        compliance_type = "NOT_COMPLIANT"
                        self.annotation = ("<p>This bucket's policy does not disallow connections over HTTP.</p>"
                                           "<p>There is no SecureTransport condition in this bucket's policy, "
                                           "meaning you cannot prevent non-HTTPS connections to your bucket, "
                                           "which poses a security risk.</p>")
                        break
            else:
                compliance_type = "COMPLIANT"
                log_string = "Bucket is compliant"

        evaluation = self.build_evaluation(
            "root",
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )

        self.app.log.debug(log_string)
        return evaluation
