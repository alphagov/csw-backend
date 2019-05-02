# AwsS3Versioning
# extends GdsS3Client
# Checks to see if an S3 bucket has versioning enabled

from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_s3_client import GdsS3Client


class AwsS3Versioning(CriteriaDefault):

    active = True

    ClientClass = GdsS3Client

    resource_type = "AWS::S3::Bucket"

    is_regional = False

    title = "S3 Buckets: Bucket Versioning Enabled"
    description = "Checks that all S3 buckets have versioning enabled."
    why_is_it_important = (
        "Versioning in S3 is a way to recover from unintended user changes and actions that might "
        "occur through misuse or corruption, such as ransomware infection. Each time an object "
        "changes, a new version of that object is created."
    )
    how_do_i_fix_it = (
        "Enable versioning on the S3 buckets listed above. Please see the following AWS documentation "
        "to enable versioning for an S3 bucket:<br />"
        "<a href='https://docs.aws.amazon.com/AmazonS3/latest/user-guide/enable-versioning.html'>"
        "https://docs.aws.amazon.com/AmazonS3/latest/user-guide/enable-versioning.html</a>"
    )

    def __init__(self, app):
        super(AwsS3Versioning, self).__init__(app)

    def get_data(self, session, **kwargs):
        self.app.log.debug("Getting a list of buckets")
        buckets = self.client.get_bucket_list(session)
        for bucket in buckets:
            # Mutating items as I'm iterating over them again... Sorry
            bucket["Versioning"] = self.client.get_bucket_versioning(
                session, bucket["Name"]
            )

        return buckets

    def translate(self, data):
        item = {
            "resource_id": "arn:aws:s3:::" + data.get("Name", ""),
            "resource_name": data.get("Name", ""),
        }

        return item

    def evaluate(self, event, bucket, whitelist=[]):
        log_string = ""
        if bucket["Versioning"] is None:
            compliance_type = "NON_COMPLIANT"
            self.annotation = "Unable to retrieve versioning status for this bucket."
            log_string = "The call to get bucket versioning failed."
        elif "Status" in bucket["Versioning"]:
            if bucket["Versioning"]["Status"] == "Enabled":
                self.annotation = ""
                compliance_type = "COMPLIANT"
                log_string = "Bucket is found to be compliant."
            else:
                compliance_type = "NON_COMPLIANT"
                self.annotation = "This S3 bucket has versioning suspended."
                log_string = "Bucket has a Status key in its versioning data, but it does not have the 'Enabled' value."
        else:
            compliance_type = "NON_COMPLIANT"
            self.annotation = "This S3 bucket does not have versioning enabled."
            log_string = "Bucket does not have a Status key in its versioning data, implying it is not enabled."

        evaluation = self.build_evaluation(
            ("arn:aws:s3:::" + bucket["Name"]),
            compliance_type,
            event,
            self.resource_type,
            self.annotation,
        )
        self.app.log.debug(log_string)
        return evaluation
