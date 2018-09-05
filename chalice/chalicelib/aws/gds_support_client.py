# GdsSupportClient
# extends GdsAwsClient
# implements aws support endpoint queries for Trusted Advisor data

from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsSupportClient(GdsAwsClient):

    # list buckets
    def describe_trusted_advisor_checks(self, session):

        support = self.get_boto3_session_client('support', session, 'us-east-1')
        response = support.describe_trusted_advisor_checks(language='en')
        checks = response['checks']

        return checks

    def describe_trusted_advisor_check_result(self, session, check_id):

        support = self.get_boto3_session_client('support', session, 'us-east-1')
        response = support.describe_trusted_advisor_check_result(
            checkId=check_id,
            language='en'
        )

        result = response['result']
        return result
