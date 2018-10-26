"""
implements aws::couldtrail::logging
"""

from chalicelib.criteria.criteria_default import CriteriaDefault


class AwsCouldtrailLogging(CriteriaDefault):
    """
    """

    def get_data(self, session, **kwargs):
        """
        """
        return

    def translate(self, data):
        """
        """
        return

    def evaluate(self, event, item, whitelist=[]):
        """
        The event parameter is the lambda dictionary triggering this criterion
        and must be passed unmodified to the return dictionary.
        The item parameter is the value of the result key of the
        support API method called describe_trusted_advisor_check_result.
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/support.html#Support.Client.describe_trusted_advisor_check_result
        """
        event = {}
        resource_id = None
        compliance_type = None
        #TODO: logic to determine resource_id, compliance_type
        #TODO: also here we will determine the annotation
        return self.build_evaluation(
            resource_id,
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )
