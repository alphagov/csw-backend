from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_s3_client import GdsS3Client


class AwsS3DefaultEncryptionAtRest(CriteriaDefault):
    active = True

    ClientClass = GdsS3Client

    is_regional = False

    resource_type = "AWS::S3::Bucket"

    title = "S3 Buckets: Encryption Enabled at Rest"

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
            bucket['Encryption'] = self.client.get_bucket_encryption(session, bucket['Name'])
        return buckets

    def translate(self, data):

        item = {
            "resource_id": 'arn:aws:s3:::' + data.get('Name', ''),
            "resource_name": data.get('Name', '')
        }

        return item

    def evaluate(self, event, bucket, whitelist=[]):
        self.app.log.debug(f"Evaluating bucket with name {bucket['Name']}")
        if isinstance(bucket['Encryption'], dict):
            compliance_type = "COMPLIANT"
            self.app.log.debug("Bucket found compliant")
        else:
            compliance_type = "NOT_COMPLIANT"
            self.annotation = "The S3 bucket does not have encryption at rest enabled."
            self.app.log.debug("Bucket is found to be not compliant")

        evaluation = self.build_evaluation(
            ('arn:aws:s3:::' + bucket['Name']),
            compliance_type,
            event,
            self.resource_type,
            self.annotation)
        return evaluation
