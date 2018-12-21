"""
implements aws::couldtrail::logging
checkId: vjafUGJ9H0
TA checks for cloudtrail being turned on in all regions and without errors.
Also checks if CST receives the trails in its predefined bucket.
"""
import json

from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_support_client import GdsSupportClient


class CouldtrailLogging(CriteriaDefault):
    """
    """
    active = False

    def __init__(self, app):
        # attributes to overwrite in subclasses
        self.status_string = ''
        self.status_interval = ''
        # attributes common in both subclasses
        self.resource_type = 'AWS::Cloudtrail::Logging'
        self.ClientClass = GdsSupportClient
        self.check_id = 'vjafUGJ9H0'
        self.language = 'en'
        self.region = 'us-east-1'
        self.annotation = ''
        super(CouldtrailLogging, self).__init__(app)

    def get_data(self, session, **kwargs):
        output = self.client.describe_trusted_advisor_check_result(
            session,
            checkId=self.check_id,
            language=self.language
        )
        self.app.log.debug(json.dumps(output))
        return output['flaggedResources']  # will have len() == 0 if compliant or non-applicable

    def translate(self, data={}):
        return {
            'resource_id': 'root',
            'resource_name': 'Root Account',
        }

