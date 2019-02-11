"""
implements aws::cloudtrail::logging
checkId: vjafUGJ9H0
TA checks for cloudtrail being turned on in all regions and without errors.
Also checks if CST receives the trails in its predefined bucket.
"""
from chalicelib.criteria.criteria_default import TrustedAdvisorCriterion


class CloudtrailLogging(TrustedAdvisorCriterion):
    """
    """
    active = False

    def __init__(self, app):
        self.resource_type = 'AWS::Cloudtrail::Logging'
        self.check_id = 'vjafUGJ9H0'
        super(CloudtrailLogging, self).__init__(app)

    def translate(self, data={}):
        return {
            'region': data.get('metadata', ['', ])[0],
            'resource_id': data.get('resourceId', ''),
            'resource_name': data.get('metadata', ['', '', ])[1],  # trail name or empty string
        }


class CloudtrailLogHasErrors(CloudtrailLogging):
    """
    TODO
    """
    active = True

    def __init__(self, app):
        self.title = 'CloudTrail: Logs delivered without errors'
        self.description = (
            'CloudTrail reports that there are errors in delivering the logs to an S3 bucket.'
        )
        self.why_is_it_important = (
            'CloudTrail keeps logs of API calls made on your AWS account.<br />'
            'These logs allow closer monitoring of activity, '
            'to make sure that users and resources are not behaving incorrectly.<br />'
            'Because of this, it is important to make sure CloudTrail is not misconfigured.'
        )
        self.how_do_i_fix_it = (
            'Make sure that the S3 bucket that CloudTrail targets exists '
            '- if it gets removed, the logs can’t be delivered.<br />'
            'Make sure that CloudTrail has write permissions for the bucket it’s trying to deliver its logs to.'
        )
        super(CloudtrailLogHasErrors, self).__init__(app)

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


class CloudtrailLogNotInRegion(CloudtrailLogging):
    """
    TODO
    """
    active = True

    def __init__(self, app):
        self.title = 'CloudTrail: Logging is turned on in all regions'
        self.description = (
            'A trail has not been created for a region in your account.'
        )
        self.why_is_it_important = (
            'CloudTrail keeps logs of API calls made on your AWS account.<br />'
            'These logs allow closer monitoring of activity, '
            'to make sure that users and resources are not behaving incorrectly.<br />'
            'Because of this, it is important to make sure CloudTrail is not misconfigured.'
        )
        self.how_do_i_fix_it = (
            'Make sure you enable CloudTrail in every region.'
        )
        super(CloudtrailLogNotInRegion, self).__init__(app)

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


class CloudtrailLogTurnedOff(CloudtrailLogging):
    """
    TODO
    """
    active = True

    def __init__(self, app):
        self.title = 'CloudTrail: All configured trails are turned on'
        self.description = (
            'Logging is turned off for a trail in your account.'
        )
        self.why_is_it_important = (
            'CloudTrail keeps logs of API calls made on your AWS account.<br />'
            'These logs allow closer monitoring of activity, '
            'to make sure that users and resources are not behaving incorrectly.<br />'
            'Because of this, it is important to make sure CloudTrail is not misconfigured.'
        )
        self.how_do_i_fix_it = (
            'Make sure that logging is switched on for all regions.'
        )
        super(CloudtrailLogTurnedOff, self).__init__(app)

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


class CloudtrailLogNotToCST(CloudtrailLogging):
    """
    Subclass checking if the cloud trail is sent to the cst bucket declared here.
    """
    active = True
    cst_bucket_name = 'cyber-security-staging-csw-cloudtrail'

    def __init__(self, app):
        self.title = 'CloudTrail: A trail is configured to the Cyber Security Team'
        self.description = (
            'Logs from CloudTrail are not being delivered to the Cloud Security Team’s S3 bucket.'
        )
        self.why_is_it_important = (
            'CloudTrail keeps logs of API calls made on your AWS account.<br />'
            'These logs allow closer monitoring of activity, '
            'to make sure that users and resources are not behaving incorrectly.<br />'
            'If these logs are not delivered to the Cyber Security Team, '
            'we will not be able to monitor and review what happens in the case of an incident.'
        )
        self.how_do_i_fix_it = (
            'Set up CloudTrail to deliver logs to the Cyber Security Team bucket, at [S3 BUCKET URL].<br />'
            'To do this, you can add these lines to '
            'your internal configuration management tool (Terraform, Ansible, etc): [MAGIC LINES]'
        )
        super(CloudtrailLogNotToCST, self).__init__(app)

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
