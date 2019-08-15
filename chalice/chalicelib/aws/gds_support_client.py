# GdsSupportClient
# extends GdsAwsClient
# implements aws support endpoint queries for Trusted Advisor data
import time
from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsSupportClient(GdsAwsClient):

    # list buckets
    def describe_trusted_advisor_checks(self, session):

        try:
            self.app.log.debug("describe trusted advisor checks")

            support = self.get_boto3_session_client("support", session, "us-east-1")

            self.app.log.debug("created boto3 client")

            response = support.describe_trusted_advisor_checks(language="en")

            self.app.log.debug("called api")

            checks = response["checks"]
        except Exception as err:
            self.app.log.error("Describe trusted advisor checks error: " + str(err))
            checks = []

        return checks

    def describe_trusted_advisor_check_result(self, session, **kwargs):

        support = self.get_boto3_session_client("support", session, "us-east-1")
        response = support.describe_trusted_advisor_check_result(**kwargs)

        result = response["result"]
        return result

    def refresh_trusted_advisor_check(self, session, **kwargs):

        support = self.get_boto3_session_client("support", session, "us-east-1")
        response = support.refresh_trusted_advisor_check(**kwargs)

        result = response["status"]
        return result

    def refresh_check_with_wait(self, session, check_id):
        updated = False
        try:
            update_status = "none"

            retries = 3
            attempt = 0
            wait_secs = 0
            # call update status a maximum of [retries] times
            while (update_status != "success") and (attempt <= retries):
                time.sleep(wait_secs)

                response = self.refresh_trusted_advisor_check(
                    session, checkId=check_id
                )
                update_status = response["status"]
                wait_secs = float(response["millisUntilNextRefreshable"]) / float(1000)
                attempt += 1
            updated = update_status == "success"

            if not updated:
                raise Exception("Not updated")
        except Exception:
            self.app.log.debug(f"Check {check_id} could not be refreshed")

        return updated
