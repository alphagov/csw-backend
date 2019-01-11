"""
implements AWS::EBS::PublicSnapshots
checkId: ePs02jT06w
"""
from chalicelib.criteria.criteria_default import TrustedAdvisorCriterion


class EBSPublicSnapshot(TrustedAdvisorCriterion):
    """
    """
    active = True

    def __init__(self, app):
        self.resource_type = 'AWS::EBS::PublicSnapshots'
        self.check_id = 'xSqX82fQu'
        self.title = 'EBS Public Snapshots'
        self.description = (
            ''
        )
        self.why_is_it_important = (
            ''
        )
        self.how_do_i_fix_it = (
            ''
        )
        super(EBSPublicSnapshot, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = 'COMPLIANT'
        # if item["metadata"][2] == 'Yellow':
        #     compliance_type = 'NON_COMPLIANT'
        #     self.annotation = (
        #         f'The security group (with ID "{item["metadata"][3]}") allows access to ports that '
        #         f'are not configured for the load balancer "{item["metadata"][1]}" in region "{item["metadata"][0]}".'
        #     )
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )
