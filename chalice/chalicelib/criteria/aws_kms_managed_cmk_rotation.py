"""
"""
from chalicelib.aws.gds_kms_client import GdsKmsClient
from chalicelib.criteria.criteria_default import CriteriaDefault


class ManagedCmkRotation(CriteriaDefault):
    """
    """
    def __init__(self, app):
        super(ManagedCmkRotation, self).__init__(app)

    def get_data(self, session, **kwargs):
        pass

    def translate(self, data={}):
        pass

    def evaluate(self, event, item, whitelist=[]):
        pass
