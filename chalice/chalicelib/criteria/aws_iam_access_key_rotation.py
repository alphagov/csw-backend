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
        self.active = True
        self.resource_type = 'AWS::*::*'
        self.check_id = 'DqdJqYeRm5'
        self.language = 'en'
        self.region = 'us-east-1'
        self.annotation = ''
        self.title = None
        self.description = None
        self.why_is_it_important = None
        self.how_do_i_fix_it = None

    def get_data(self, session, **kwargs):
        """
        """
        return

    def translate(self, data={}):
        """
        """
        return {
            'resource_id': 'root',
            'resource_name': 'Root Account',
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
        if item['result']['status'] == 'ok':
            compliance_type = 'COMPLIANT'
        else:  # construct annotation
            self.annotation = '<p>STATUS: {}</p><ol>'.format(
                item['result']['status'].upper()
            )
            for flagged_resource in item['result']['flaggedResources']:
                if flagged_resource['metadata'][0] != 'Green':
                    self.annotation += '{} {} {} {} {}'.format(
                        *flagged_resource['metadata']
                    )
            self.annotation += '</ol>'
        return self.build_evaluation(
            self.translate()['resource_id'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )
