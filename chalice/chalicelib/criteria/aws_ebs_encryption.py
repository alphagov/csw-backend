"""
"""
from chalicelib.aws.gds_ec2_client import GdsEc2Client
from chalicelib.criteria.criteria_default import CriteriaDefault


class EbsEncryption(CriteriaDefault):
    """
    """
    active = True
    ClientClass = GdsEc2Client
    is_regional = True
    resource_type = 'AWS::EBS::ENCRYPTION'
    title = 'EBS: Encryption Enabled'
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
        return

    def translate(self, data={}):
        return {
            'region': data['TODO::REGION'],
            'resource_id': data['TODO::ID'],
            'resource_name': data['TODO::NAME'],
        }

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = ''
        return self.build_evaluation(
            'TODO::ID',
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )
