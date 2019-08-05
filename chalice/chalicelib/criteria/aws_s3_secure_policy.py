# AwsS3SecurePolicy
# extends CriteriaDefault
# Checks if there is a policy in each bucket in the target account
from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_s3_client import GdsS3Client
import json


class AwsS3SecurePolicy(CriteriaDefault):

    active = True
    severity = 3

    ClientClass = GdsS3Client

    resource_type = ""

    is_regional = False

    title = "S3 - Insecure Bucket Policies"

    description = (
        "Checks that all S3 buckets have policies with the condition 'aws:SecureTransport' to ensure that data is sent "
        "or retrieved from the bucket over encrypted https rather than in plain text."
    )

    why_is_it_important = (
        "When S3 buckets are not configured to strictly require SSL connections, the communication "
        "between the clients (users, applications) and these buckets is vulnerable to eavesdropping "
        "and man-in-the-middle (MITM) attacks."
    )

    how_do_i_fix_it = (
        "Define an access policy that will enforce SSL-only (encrypted) access to your S3 data, "
        "especially when dealing with sensitive or private data. Then, set the condition "
        "'aws:SecureTransport' in your S3 policy to enforce HTTPS requests to your buckets. An "
        "example of a S3 policy can be found in the AWS blog below:<br />"
        "<a href='https://aws.amazon.com/blogs/security/how-to-use-bucket-policies-and-apply-defense-in-"
        "depth-to-help-secure-your-amazon-s3-data/'>https://aws.amazon.com/blogs/security/how-to-use-buc"
        "ket-policies-and-apply-defense-in-depth-to-help-secure-your-amazon-s3-data/</a>"
    )

    fail = "Bucket does not enforce SecureTransport"

    def __init__(self, app):
        super(AwsS3SecurePolicy, self).__init__(app)

    def get_data(self, session, **kwargs):
        """Request buckets and policies from AWS API."""
        buckets = self.client.get_bucket_list(session)
        for bucket in buckets:
            policy = self.client.get_bucket_policy(session, bucket["Name"])
            try:
                bucket["Policy"] = json.loads(policy)
            except (TypeError, json.decoder.JSONDecodeError):
                pass

        return buckets

    def translate(self, data):
        """But why?"""
        return {
            "resource_id": "arn:aws:s3:::" + data.get("Name", ""),
            "resource_name": data.get("Name", ""),
        }

    def compliance_words(self, compliant):
        """Return the Config compatible compliance type in words."""
        return "COMPLIANT" if compliant else "NON_COMPLIANT"


    def get_bucket_securetransport_statements(self, bucket):
        """Return a list of policy statements that have a SecureTransport
        condition."""
        statements = []
        try:
            for statement in bucket["Policy"]["Statement"]:
                if "Condition" not in statement:
                    continue
                for k, v in statement["Condition"].items():
                    if "aws:SecureTransport" in v.keys():
                        statements.append(statement)
        except:
            pass
        return statements

    def evaluate(self, event, bucket, whitelist=[]):
        """Evaluate the bucket policy to check that it requires
        SecureTransport."""
        compliant = False
        annotation = self.fail
        bucket_arn = f"arn:aws:s3:::{bucket['Name']}"

        statements = self.get_bucket_securetransport_statements(bucket)

        for statement in statements:
            try:
                # If bucket allows in-SecureTransport then fail.
                if (
                    statement["Resource"] != f"{bucket_arn}/*"
                    and statement["Condition"]["Bool"]["aws:SecureTransport"] == "false"
                ):
                    compliant = False
                    annotation = self.fail
                    break
                if statement["Resource"] == f"{bucket_arn}/*" and (
                    (
                        statement["Condition"]["Bool"]["aws:SecureTransport"] == "true"
                        and statement["Effect"] == "Allow"
                    )
                    or (
                        statement["Condition"]["Bool"]["aws:SecureTransport"] == "false"
                        and statement["Effect"] == "Deny"
                    )
                ):
                    compliant = True
                    annotation = ""
            except KeyError:
                continue

        return self.build_evaluation(
            bucket_arn,
            self.compliance_words(compliant),
            event,
            self.resource_type,
            annotation,
        )
