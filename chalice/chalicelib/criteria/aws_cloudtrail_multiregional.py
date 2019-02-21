"""
"""
from chalicelib.aws.gds_cloudtrail_client import GdsCloudtrailClient
from chalicelib.criteria.criteria_default import CriteriaDefault


class MultiregionalCloudtrail(CriteriaDefault):
    """
    """
    active = True
    ClientClass = GdsCloudtrailClient
    is_regional = False
    resource_type = 'AWS::CLOUDTRAIL:MULTIREGIONAL'
    title = 'Cloud Trail: Multi-regional'
    description = (
        'TODO'
    )
    why_is_it_important = (
        'TODO'
    )
    how_do_i_fix_it = (
        'TODO'
    )

    def __init__(self, app):
        super(MultiregionalCloudtrail, self).__init__(app)

    def get_data(self, session, **kwargs):
        try:
            return self.client.describe_trails(session)
        except Exception as e:
            self.app.log.error(self.app.utilities.get_typed_exception(e))
            return []

    def translate(self, data={}):
        return {
            'region': data['HomeRegion'],
            'resource_id': data['TrailARN'],
            'resource_name': data['Name'],
        }

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = 'COMPLIANT'
        self.annotation = ''
        return self.build_evaluation(
            item['TrailARN'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )
