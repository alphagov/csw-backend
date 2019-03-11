"""
"""
from chalicelib.aws.gds_elb_client import GdsElbClient
from chalicelib.criteria.criteria_default import CriteriaDefault


class ElbLogging(CriteriaDefault):
    """
    """
    active = True
    ClientClass = GdsElbClient
    is_regional = False
    resource_type = 'AWS::ELB::LOGGING'
    title = 'ELB: Logging Enabled'
    description = (
        ''
    )
    why_is_it_important = (
        ''
    )
    how_do_i_fix_it = (
        ''
    )

    def get_data(self, session, **kwargs):
        return self.client.get_balancer_list_with_attributes(session)

    def translate(self, data={}):
        return {
            'region': data['TODO'],
            'resource_id': data['TODO'],
            'resource_name': data['TODO'],
        }

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = 'TODO'
        return self.build_evaluation(
            item['TODO'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )
