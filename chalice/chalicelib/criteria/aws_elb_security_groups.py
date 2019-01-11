"""
implements aws::elb::security_groups
checkId: xSqX82fQu
TA checks for load balancers belonging to a security group.
"""
import json

from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_support_client import GdsSupportClient


class ELBSecurityGroups(CriteriaDefault):
    """
    Superclass for both checks.
    """
    active = False

    def __init__(self, app):
        # attributes to overwrite in subclasses
        self.status_string = ''
        self.status_interval = ''
        # attributes common in both subclasses
        self.resource_type = 'AWS::ELB::SecurityGroups'
        self.ClientClass = GdsSupportClient
        self.check_id = 'xSqX82fQu'
        self.language = 'en'
        self.region = 'us-east-1'
        self.annotation = ''
        super(ELBSecurityGroups, self).__init__(app)

    def get_data(self, session, **kwargs):
        pass

    def translate(self, data={}):
        pass


class ELBSecurityGroupsYellow(ELBSecurityGroups):
    """
    Subclass checking for port mismatch between the ELB and VPC.
    """
    def __init__(self, app):
        super(ELBSecurityGroupsYellow, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        pass


class ELBSecurityGroupsRed(ELBSecurityGroups):
    """
    Subclass checking for existance of a security group for the ELB.
    """
    def __init__(self, app):
        super(ELBSecurityGroupsRed, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        pass
