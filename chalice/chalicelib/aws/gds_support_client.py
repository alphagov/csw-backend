# GdsSupportClient
# extends GdsAwsClient
# implements aws support endpoint queries for Trusted Advisor data
import boto3

from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsSupportClient(GdsAwsClient):

    # list buckets
    def describe_trusted_advisor_checks(self, session):

        try:
            self.app.log.debug('describe trusted advisor checks')

            #support = boto3.client('support', region_name='us-east-1')
            support = self.get_boto3_session_client('support', session, 'us-east-1')

            self.app.log.debug('created boto3 client')

            response = support.describe_trusted_advisor_checks(language='en')

            self.app.log.debug('called api')

            checks = response['checks']
        except Exception as err:
            self.app.log.error('Describe trusted advisor checks error: ' + str(err))
            checks = []

        return checks

    def describe_trusted_advisor_check_result(self, session, check_id):

        support = self.get_boto3_session_client('support', session, 'us-east-1')
        response = support.describe_trusted_advisor_check_result(
            checkId=check_id,
            language='en'
        )

        result = response['result']
        return result
