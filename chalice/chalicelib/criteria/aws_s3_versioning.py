# AwsS3Versioning
# extends GdsS3Client
# Checks to see if an S3 bucket has versioning enabled

from chalicelib.criteria.criteria_default import CriteriaDefault


class AwsS3Versioning(CriteriaDefault):

    active = True

    def evaluate(self):
        pass
