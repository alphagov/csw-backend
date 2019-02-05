"""
implements aws::iam::access_key_rotation
checkId: DqdJqYeRm5
The access key is active and has been rotated in the past 90 days (yellow/warning) or 2 years (red/error).
"""
from chalicelib.criteria.criteria_default import TrustedAdvisorCriterion


class AwsIamAccessKeyRotationBase(TrustedAdvisorCriterion):
    """
    Base class, don't subclass this, use the two subclasses declared below.
    """
    active = False

    def __init__(self, app):
        self.resource_type = 'AWS::iam::access_key_rotation'
        self.check_id = 'DqdJqYeRm5'
        self.title = " Outdated IAM access keys"
        self.why_is_it_important = (
            'Rotating IAM credentials periodically will significantly reduce the chances that a compromised set of '
            'access keys can be used without your knowledge to access certain components within your AWS account.'
        )
        super(AwsIamAccessKeyRotationBase, self).__init__(app)

    def translate(self, data={}):
        """
        Unlike other TA checks here we overwrite translate to return the access key, instead of the standard resource.
        """
        return {
            'resource_id': data.get('resourceId', ''),
            'resource_name': data.get('metadata', ['', '', '', ])[2],  # access key or empty string
        }


class AwsIamAccessKeyRotationYellow(AwsIamAccessKeyRotationBase):
    """
    Base class, don't subclass this, use the two subclasses declared below.
    """
    active = True

    def __init__(self, app):
        super(AwsIamAccessKeyRotationYellow, self).__init__(app)
        self.description = (
            'At least one active Identity and Access Management '
            f'(IAM) access key has not been rotated in the last 90 days.'
        )
        self.how_do_i_fix_it = (
            'Ensure that all your IAM user access keys are rotated at least every 90 days in order to  '
            'decrease the likelihood of accidental exposures and protect your AWS resources '
            'against unauthorized access. <br />To rotate access keys, it is recommended to follow these steps: <ol>'
            '<li>Create a second access key in addition to the one in use.</li>'
            '<li>Update all your applications to use the new access key and validate that the applications are working.</li>'
            '<li>Change the state of the previous access key to inactive.</li>'
            '<li>Validate that your applications are still working as expected.</li>'
            '<li>Delete the inactive access key.</li>'
            '</ol>'
        )

    def evaluate(self, event, item, whitelist=[]):
        """
        The event parameter is the lambda dictionary triggering this criterion
        and must be passed unmodified to the return dictionary.
        The item parameter is the value of the result key of the
        support API method called describe_trusted_advisor_check_result.
        """
        if item['status'] in ['warning', 'error']:
            compliance_type = 'NON_COMPLIANT'
            self.annotation = (
                f'User "{item["metadata"][1]}" has not rotated access key '
                f'"{item["metadata"][2]}" for more than 90 days'
            )
        else:
            compliance_type = 'COMPLIANT'
            self.annotation = ''
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )


class AwsIamAccessKeyRotationRed(AwsIamAccessKeyRotationBase):
    """
    Base class, don't subclass this, use the two subclasses declared below.
    """
    active = True

    def __init__(self, app):
        super(AwsIamAccessKeyRotationRed, self).__init__(app)
        self.description = (
            'At least one active Identity and Access Management '
            f'(IAM) access key has not been rotated in the last 2 years.'
        )
        self.how_do_i_fix_it = (
            'Ensure that all your IAM user access keys are rotated at least every 2 years in order to  '
            'decrease the likelihood of accidental exposures and protect your AWS resources '
            'against unauthorized access. <br />To rotate access keys, it is recommended to follow these steps: <ol>'
            '<li>Create a second access key in addition to the one in use.</li>'
            '<li>Update all your applications to use the new access key and validate that the applications are working.</li>'
            '<li>Change the state of the previous access key to inactive.</li>'
            '<li>Validate that your applications are still working as expected.</li>'
            '<li>Delete the inactive access key.</li>'
            '</ol>'
        )

    def evaluate(self, event, item, whitelist=[]):
        """
        The event parameter is the lambda dictionary triggering this criterion
        and must be passed unmodified to the return dictionary.
        The item parameter is the value of the result key of the
        support API method called describe_trusted_advisor_check_result.
        """
        compliance_type = 'COMPLIANT'
        if item['status'] == 'error':
            compliance_type = 'NON_COMPLIANT'
            self.annotation = (
                f'User "{item["metadata"][1]}" has not rotated access key '
                f'"{item["metadata"][2]}" for more than 2 years'
            )
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )
