"""
implements aws::iam::access_key_rotation
checkId: DqdJqYeRm5
The access key is active and has been rotated in the past 90 days (yellow/warning) or 2 years (red/error).
"""
from chalicelib.criteria.criteria_default import TrustedAdvisorCriterion


class AwsIamExposedAccessKey(TrustedAdvisorCriterion):
    """
    Subclass Criterion checking for (potentially) exposed access keys.
    """
    active = False

    def __init__(self, app):
        self.resource_type = 'AWS::iam::exposed_key'
        self.check_id = '12Fnkpl8Y5'
        self.description = (
            'Checks that there are no IAM Access Keys and their corresponding Secrets committed to common code '
            'repositories like GitHub.'
        )
        self.why_is_it_important = (
            'Access keys are what allow AWS users to authenticate themselves so that they can make use of certain '
            'functions within AWS, such as making API calls, '
            'or using the AWS command line interface to query the account, make or remove resources, and so on. <br />'
            'If these access keys are leaked, '
            'attackers may gain a better understanding of how your account is structured, '
            'and they may steal and/or vandalise data within your account.'
        )
        super(AwsIamExposedAccessKey, self).__init__(app)

    def translate(self, data={}):
        """
        Unlike other TA checks here we overwrite translate to return the access key, instead of the standard resource.
        """
        return {
            'resource_id': data.get('resourceId', ''),
            'resource_name': data.get('metadata', ['', ])[0],  # access key ID
        }


class AwsIamPotentiallyExposedAccessKey(AwsIamExposedAccessKey):
    """
    Subclass Criterion checking for (potentially) exposed access keys.
    """
    active = True

    def __init__(self, app):
        self.title = 'IAM Access Keys: Access keys have not been exposed on the internet'
        self.how_do_i_fix_it = (
            'Delete the affected access key, and generate a new one '
            'for the user or application. <br />Please follow the below recommendations accordingly:<br />'
            '- DELETE THE KEY (for IAM users)<br />'
            'Navigate to your IAM Users list in the AWS Management Console, '
            '<a href="https://console.aws.amazon.com/iam/home#users">here</a>.<br />'
            'Please select the IAM user identified above. Click on the "User Actions" drop-down menu '
            'and then click "Manage Access Keys" to show that user\'s active Access Keys. '
            'Click "Delete" next to the access key identified above.'
            '- ROTATE THE KEY (for applications)<br />'
            'If your application uses the access key, you need to replace the exposed key with a new one.<br />'
            'To do this, first create a second key (at that point both keys will be active) '
            'and modify your application to use the new key.<br />'
            'Then disable (but do not delete) the first key.<br />'
            'If there are any problems with your application, you can make the first key active again.<br />'
            'When your application is fully functional with the first key inactive, please delete the first key.<br />'
            'We strongly encourage you to immediately review your AWS account for any unauthorized AWS usage, '
            'suspect running instances, or inappropriate IAM users and policies.<br />'
            'To review any unauthorized access, '
            'please inspect CloudTrail logs to see what was done with the access key while it was leaked '
            'and also Investigate how the access key was leaked, '
            'and take steps to prevent it from happening again.<br />'
        )
        super(AwsIamPotentiallyExposedAccessKey, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        """
        The event parameter is the lambda dictionary triggering this criterion
        and must be passed unmodified to the return dictionary.
        The item parameter is the value of the result key of the
        support API method called describe_trusted_advisor_check_result.
        """
        compliance_type = 'NON_COMPLIANT'
        if item['metadata'][2] == 'Exposed':
            self.annotation = (
                'Exposed - AWS has identified an access key ID and corresponding secret access key '
                f'"{item["metadata"][0]}" that have been exposed on the Internet.'
            )
        elif item['metadata'][2] == 'Suspected':
            compliance_type = 'COMPLIANT'
        else:
            self.annotation = (
                'Potentially compromised - AWS has identified an access key ID and corresponding secret access key '
                '"{item["metadata"][0]}" that have been exposed '
                'on the Internet and may have been compromised (used).'
            )
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )


class AwsIamSuspectedExposedAccessKey(AwsIamExposedAccessKey):
    """
    Subclass Criterion checking for suspected exposed access keys.
    """
    active = True

    def __init__(self, app):
        self.title = 'IAM Access Keys: There is no irregular EC2 activity to suggest an exposed key'
        self.how_do_i_fix_it = 'Alert not actionable'
        super(AwsIamSuspectedExposedAccessKey, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        """
        The event parameter is the lambda dictionary triggering this criterion
        and must be passed unmodified to the return dictionary.
        The item parameter is the value of the result key of the
        support API method called describe_trusted_advisor_check_result.
        """
        compliance_type = 'NON_COMPLIANT'
        if item['metadata'][2] == 'Suspected':
            self.annotation = (
                f'Suspected - Irregular Amazon EC2 usage indicates that the access key "{item["metadata"][0]}" '
                'may have been compromised, but it has not been identified as exposed on the Internet.'
            )
        else:
            compliance_type = 'COMPLIANT'
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )
