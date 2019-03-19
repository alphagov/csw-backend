from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_s3_client import GdsS3Client


class AwsS3DefaultEncryptionAtRest(CriteriaDefault):
    active = True

    def evaluate(self, event, item, whitelist=[]):
        pass
