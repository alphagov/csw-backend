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
            'resource_id': data['resourceId'],
            'resource_name': data['metadata'][1],  # trail name
        }


class CouldtrailLogHasErrors(CouldtrailLogging):
    """
    TODO
    """
    active = True

    def __init__(self, app):
        self.title = ''
        self.description = (
            ''
        )
        self.why_is_it_important = (
            ''
        )
        self.how_do_i_fix_it = (
            ''
        )
        super(CouldtrailLogHasErrors, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = 'COMPLIANT'
        if item["metadata"][4] is not None:
            compliance_type = 'NON_COMPLIANT'
            self.annotation = (
                f'The cloudtrail {item["metadata"][1]} in region {item["metadata"][0]} has errors, '
                f'the last one was: "{item["metadata"][4]}"'
            )
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )


class CouldtrailLogNotInRegion(CouldtrailLogging):
    """
    TODO
    """
    active = True

    def __init__(self, app):
        self.title = ''
        self.description = (
            ''
        )
        self.why_is_it_important = (
            ''
        )
        self.how_do_i_fix_it = (
            ''
        )
        super(CouldtrailLogNotInRegion, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = 'COMPLIANT'
        if item["metadata"][2] == 'Off':
            compliance_type = 'NON_COMPLIANT'
            self.annotation = f'Cloudtrail {item["metadata"][1]} is deactivated in region {item["metadata"][0]}'
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )


class CouldtrailLogTurnedOff(CouldtrailLogging):
    """
    TODO
    """
    active = True

    def __init__(self, app):
        self.title = ''
        self.description = (
            ''
        )
        self.why_is_it_important = (
            ''
        )
        self.how_do_i_fix_it = (
            ''
        )
        super(CouldtrailLogTurnedOff, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = 'COMPLIANT'
        if item["metadata"][1] is None or item["metadata"][2] == 'Not enabled' or item["metadata"][3] is None:
            compliance_type = 'NON_COMPLIANT'
            self.annotation = 'Cloudtrail is turned off!'
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )


class CouldtrailLogNotToCST(CouldtrailLogging):
    """
    Subclass checking if the cloud trail is sent to the cst bucket declared here.
    """
    active = True
    cst_bucket_name = 'cyber-security-staging-csw-cloudtrail'

    def __init__(self, app):
        self.title = ''
        self.description = (
            ''
        )
        self.why_is_it_important = (
            ''
        )
        self.how_do_i_fix_it = (
            ''
        )
        super(CouldtrailLogNotToCST, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = 'NON_COMPLIANT'
        if item["metadata"][3] == self.cst_bucket_name:
            compliance_type = 'COMPLIANT'
        else:
            self.annotation = (
                f'Trail {item["metadata"][1]} in region {item["metadata"][0]} is not sent to {self.cst_bucket_name}'
            )
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )
