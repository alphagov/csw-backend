from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_s3_client import GdsS3Client


class AwsS3DefaultEncryptionAtRest(CriteriaDefault):
    active = True

    ClientClass = GdsS3Client

    is_regional = False

    resource_type = "AWS::S3::Bucket"

    title = "S3 - Bucket Encryption Enabled at Rest"

    description = ("The S3 bucket does have encryption enabled at rest to automatically encrypt all objects when "
                   "stored in Amazon S3")
    why_is_it_important = ("S3 buckets with default encryption will enable Amazon to encrypt your S3 data at the "
                           "bucket level instead of object level in order to protect it from attackers or unauthorized "
                           "personnel.")
    how_do_i_fix_it = ("Enable encryption during the upload process using Server-Side Encryption with either AWS "
                       "S3-managed keys (SSE-S3) or AWS KMS-managed keys (SSE-KMS).<br />"
                       "Please see the following AWS documentation to enable encryption for an S3 bucket:<br /><a "
                       "href='https://docs.aws.amazon.com/AmazonS3/latest/user-guide/default-bucket-encryption.html'>"
                       "https://docs.aws.amazon.com/AmazonS3/latest/user-guide/default-bucket-encryption.html</a>")

    def get_data(self, session, **kwargs):
        self.app.log.debug("Getting a list of buckets in this account")
        buckets = self.client.get_bucket_list(session)
        self.app.log.debug("Adding an 'Encryption' key to these buckets")
        for bucket in buckets:
            bucket['Encryption'] = self.client.get_bucket_policy(session, bucket['Name'])
        return buckets

    def evaluate(self, event, bucket, whitelist=[]):
        self.annotation = ""
        compliance_type = ""
        evaluation = self.build_evaluation(
            ('arn:aws:s3:::' + bucket['Name']),
            compliance_type,
            event,
            self.resource_type,
            self.annotation)
        return evaluation
