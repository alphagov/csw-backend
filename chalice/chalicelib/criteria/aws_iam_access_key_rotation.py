"""
implements aws::iam::access_key_rotation
checkId: DqdJqYeRm5
"""

from chalicelib.criteria.criteria_default import CriteriaDefault


class AwsIamAccessKeyRotation(CriteriaDefault):
    """
    """

    def __init__(self, app):
        """
        """
        super(AwsIamAccessKeyRotation, self).__init__(app)

    def get_data(self, session, **kwargs):
        """
        """
        return

    def translate(self, data={}):
        """
        """
        return {
            'resource_id': None,
            'resource_name': None,
        }

    def evaluate(self, event, item, whitelist=[]):
        """
        The event parameter is the lambda dictionary triggering this criterion
        and must be passed unmodified to the return dictionary.
        The item parameter is the value of the result key of the
        support API method called describe_trusted_advisor_check_result.
        """
        # logic to determine resource_id, compliance_type
        compliance_type = None
        return self.build_evaluation(
            self.translate()['resource_id'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )
