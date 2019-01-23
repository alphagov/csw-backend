"""
"""
from chalicelib.aws.gds_ec2_security_group_client import GdsEc2SecurityGroupClient
from chalicelib.criteria.criteria_default import CriteriaDefault


class EgressRestrition(CriteriaDefault):
    """
    """
    active = True

    ClientClass = GdsEc2SecurityGroupClient

    def get_data(self, session, **kwargs):
        return self.client.describe_security_groups(session, **kwargs)

    def evaluate(self, event, item, whitelist=[]):
        """
        """
        raise
