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
        home_volumes = []
        try:
            for vol in self.client.describe_volumes(session):
                if vol['AvailabilityZone'].startswith(kwargs['region']):
                    home_volumes.append(vol)
        except Exception as e:
            self.app.log.error(self.app.utilities.get_typed_exception(e))
        return home_volumes

    def translate(self, data={}):
        return {
            'region': data['AvailabilityZone'],
            'resource_id': data['VolumeId'],
            'resource_name': data['VolumeId'],
        }

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = ''
        return self.build_evaluation(
            item['VolumeId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )
