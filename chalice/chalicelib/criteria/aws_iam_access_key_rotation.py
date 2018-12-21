"""
implements aws::iam::access_key_rotation
checkId: DqdJqYeRm5
The access key is active and has been rotated in the past 90 days (yellow/warning) or 2 years (red/error).
"""
import json

from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_support_client import GdsSupportClient


class AwsIamAccessKeyRotationBase(CriteriaDefault):
    """
    Base class, don't subclass this, use the two subclasses declared below.
    """
    active = False

    def __init__(self, app):
        # attributes to overwrite in subclasses
        self.status_string = ''
        self.status_interval = ''
        # attributes common in both subclasses
        self.resource_type = 'AWS::iam::access_key_rotation'
        self.ClientClass = GdsSupportClient
        self.check_id = 'DqdJqYeRm5'
        self.language = 'en'
        self.region = 'us-east-1'
        self.annotation = ''
        self.title = " Outdated IAM access keys"
        self.description = (
            'At least one active Identity and Access Management '
            f'(IAM) access key has not been rotated in the last {self.status_interval}.'
        )
        self.why_is_it_important = (
            'Rotating IAM credentials periodically will significantly reduce the chances that a compromised set of '
            'access keys can be used without your knowledge to access certain components within your AWS account.'
        )
        self.how_do_i_fix_it = (
            'Ensure that all your IAM user access keys are rotated at least every {self.status_interval} in order to  '
            'decrease the likelihood of accidental exposures and protect your AWS resources '
            'against unauthorized access. To rotate access keys, it is recommended to follow these steps: '
            '1) Create a second access key in addition to the one in use. '
            '2) Update all your applications to use the new access key and validate that the applications are working. '
            '3) Change the state of the previous access key to inactive. '
            '4) Validate that your applications are still working as expected. '
            '5) Delete the inactive access key.'
        )
        super(AwsIamAccessKeyRotationBase, self).__init__(app)

    def get_data(self, session, **kwargs):
        output = self.client.describe_trusted_advisor_check_result(
            session,
            checkId=self.check_id,
            language=self.language
        )
        self.app.log.debug(json.dumps(output))
        # Return as a list of 1 item for consistency with other checks
        return output['flaggedResources']

    def translate(self, data={}):
        return {
            'resource_id': data.get('resourceId', ''),
            'resource_name': data.get('metadata', ['', '', '', ])[2],  # access key or empty string
        }

    def evaluate(self, event, item, whitelist=[]):
        """
        The event parameter is the lambda dictionary triggering this criterion
        and must be passed unmodified to the return dictionary.
        The item parameter is the value of the result key of the
        support API method called describe_trusted_advisor_check_result.
        """
        # compliance_type
        compliance_type = 'NON_COMPLIANT'
        if item['status'] == 'ok':
            compliance_type = 'COMPLIANT'
        else:  # construct annotation
            self.annotation = (
                f'User "{item["metadata"][1]}" has not rotated access key '
                f'"{item["metadata"][2]}" for more than {self.status_interval}'
            )
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )


class AwsIamAccessKeyRotationYellow(AwsIamAccessKeyRotationBase):
    """
    Base class, don't subclass this, use the two subclasses declared below.
    """
    active = True

    def __init__(self, app):
        super(AwsIamAccessKeyRotationYellow, self).__init__(app)
        self.status_string = 'Yellow'
        self.status_interval = '90 days'


class AwsIamAccessKeyRotationRed(AwsIamAccessKeyRotationBase):
    """
    Base class, don't subclass this, use the two subclasses declared below.
    """
    active = True

    def __init__(self, app):
        super(AwsIamAccessKeyRotationRed, self).__init__(app)
        self.status_string = 'Red'
        self.status_interval = '2 years'
