# AwsS3SecurePolicy
# extends CriteriaDefault
# Checks if there is a policy in each bucket in the target account
from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_s3_client import GdsS3Client
import json


class AwsS3SecurePolicy(CriteriaDefault):

    active = True

    ClientClass = GdsS3Client

    resource_type = ""

    is_regional = False

    title = "S3 - Insecure Bucket Policies"

    description = (
        "Checks that all S3 buckets have policies with the condition 'aws:SecureTransport' to ensure that data is sent "
        "or retrieved from the bucket over encrypted https rather than in plain text."
    )

    why_is_it_important = ("When S3 buckets are not configured to strictly require SSL connections, the communication "
                           "between the clients (users, applications) and these buckets is vulnerable to eavesdropping "
                           "and man-in-the-middle (MITM) attacks.")

    how_do_i_fix_it = ("Define an access policy that will enforce SSL-only (encrypted) access to your S3 data, "
                       "especially when dealing with sensitive or private data. Then, set the condition "
                       "'aws:SecureTransports3bucket' in your S3 policy to enforce HTTPS requests to your buckets. An "
                       "example of a S3 policy can be found in the AWS blog below:<br />"
                       "<a href='https://aws.amazon.com/blogs/security/how-to-use-bucket-policies-and-apply-defense-in-"
                       "depth-to-help-secure-your-amazon-s3-data/'>https://aws.amazon.com/blogs/security/how-to-use-buc"
                       "ket-policies-and-apply-defense-in-depth-to-help-secure-your-amazon-s3-data/</a>")

    def __init__(self, app):
        super(AwsS3SecurePolicy, self).__init__(app)

    def get_data(self, session, **kwargs):
        self.app.log.debug("Getting a list of buckets in this account")
        buckets = self.client.get_bucket_list(session)
        self.app.log.debug("Adding a 'Policy' key to these buckets")
        for bucket in buckets:
            # I know mutating what you're iterating over is a bad idea...
            policy = self.client.get_bucket_policy(session, bucket['Name'])
            self.app.log.debug(f"policy is: '{policy}'")
            try:
                bucket['Policy'] = json.loads(policy)
            except json.decoder.JSONDecodeError:  # policy is not valid JSON - probably an exception from the client
                bucket['Policy'] = policy

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
            self.annotation = "This bucket has no policy attached."
        else:
            for statement in bucket['Policy']['Statement']:
                if 'Condition' not in statement:  # Failure: No condition
                    log_string = "Bucket does not have any conditions on its policy"
                    compliance_type = "NOT_COMPLIANT"
                    self.annotation = "This bucket's policy does not have a condition."
                    break
                else:
                    secure = statement['Condition'].get('Bool', {}).get('aws:SecureTransport')
                    if secure == "false":  # secure is either "true", "false", or None if it didn't exist
                        # Failure: HTTPS is specifically disallowed
                        log_string = "Bucket's policy condition explicitly disallows HTTPS"
                        compliance_type = "NOT_COMPLIANT"
                        self.annotation = ("This bucket's policy explicitly disallows HTTPS."
                                           "Make sure that the aws:SecureTransport condition is set to 'true'.")
                        break
                    if not secure:  # testing if secure is None
                        # Failure: no secure transport condition
                        log_string = "Bucket does not disallow insecure connections"
                        compliance_type = "NOT_COMPLIANT"
                        self.annotation = ("This bucket's policy does not disallow connections over HTTP, because "
                                           "there is no SecureTransport condition in this bucket's policy.")
                        break
            else:
                compliance_type = "COMPLIANT"
                log_string = "Bucket is compliant"

        evaluation = self.build_evaluation(
            ('arn:aws:s3:::' + bucket['Name']),
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )

        self.app.log.debug(log_string)
        return evaluation
