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
            'resource_id': data.get('resourceId', ''),
            'resource_name': data.get('metadata', ['', '', ])[1],  # trail name or None
        }


class CouldtrailLogHasErrors(CouldtrailLogging):
    """
    TODO
    """
    active = True

    def __init__(self, app):
        self.title = 'Cloudtrail Logging: Delivery Errors'
        self.description = (
            'CloudTrail reports that there are errors in delivering the logs to an S3 bucket.'
        )
        self.why_is_it_important = (
            'CloudTrail keeps logs of API calls made on your AWS account. '
            'These logs allow closer monitoring of activity, '
            'to make sure that users and resources are not behaving incorrectly. '
            'Because of this, it is important to make sure CloudTrail is not misconfigured.'
        )
        self.how_do_i_fix_it = (
            'Make sure that the S3 bucket that CloudTrail targets exists '
            '- if it gets removed, the logs can’t be delivered. '
            'Make sure that CloudTrail has write permissions for the bucket it’s trying to deliver its logs to.'
        )
        super(CouldtrailLogHasErrors, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = 'COMPLIANT'
        if item["metadata"][4] is not None:
            compliance_type = 'NON_COMPLIANT'
            self.annotation = (
                f'The cloudtrail {item["metadata"][1]} in region {item["metadata"][0]} has errors, '
                f'the last one being: "{item["metadata"][4]}".'
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
        self.title = 'Cloudtrail Logging: Turned off in a region'
        self.description = (
            'A trail has not been created for a region in your account.'
        )
        self.why_is_it_important = (
            'CloudTrail keeps logs of API calls made on your AWS account. '
            'These logs allow closer monitoring of activity, '
            'to make sure that users and resources are not behaving incorrectly. '
            'Because of this, it is important to make sure CloudTrail is not misconfigured.'
        )
        self.how_do_i_fix_it = (
            'Make sure you enable CloudTrail in every region.'
        )
        super(CouldtrailLogNotInRegion, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = 'COMPLIANT'
        if item["metadata"][2] != 'On':  # alternatively =='Off' if you don't want it triggered when trail disabled
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
        self.title = '"Cloudtrail Logging: Not activated'
        self.description = (
            'Logging is turned off for a trail in your account.'
        )
        self.why_is_it_important = (
            'CloudTrail keeps logs of API calls made on your AWS account. '
            'These logs allow closer monitoring of activity, '
            'to make sure that users and resources are not behaving incorrectly. '
            'Because of this, it is important to make sure CloudTrail is not misconfigured.'
        )
        self.how_do_i_fix_it = (
            'Make sure that logging is switched on for all regions.'
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
        self.title = 'Cloudtrail Logging: Not sent to CST'
        self.description = (
            'Logs from CloudTrail are not being delivered to the Cloud Security Team’s S3 bucket.'
        )
        self.why_is_it_important = (
            'CloudTrail keeps logs of API calls made on your AWS account. '
            'These logs allow closer monitoring of activity, '
            'to make sure that users and resources are not behaving incorrectly. '
            'If these logs are not delivered to the Cyber Security Team, '
            'we will not be able to monitor and review what happens in the case of an incident.'
        )
        self.how_do_i_fix_it = (
            'Set up CloudTrail to deliver logs to the Cyber Security Team bucket, at [S3 BUCKET URL]. '
            'To do this, you can add these lines to '
            'your internal configuration management tool (Terraform, Ansible, etc): [MAGIC LINES]'
        )
        super(CouldtrailLogNotToCST, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = 'COMPLIANT'
        if item["metadata"][3] != self.cst_bucket_name:
            compliance_type = 'NON_COMPLIANT'
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
