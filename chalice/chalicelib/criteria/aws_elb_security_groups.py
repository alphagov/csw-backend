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
        output = self.client.describe_trusted_advisor_check_result(
            session,
            checkId=self.check_id,
            language=self.language
        )
        self.app.log.debug(json.dumps(output))
        return output['flaggedResources']  # will have len() == 0 if compliant or non-applicable

    def translate(self, data={}):
        return {
            'resource_id': data.get('resourceId', ''),
            'resource_name': data.get('metadata', ['', '', ])[1],  # trail name or empty string
        }


class ELBSecurityGroupsYellow(ELBSecurityGroups):
    """
    Subclass checking for port mismatch between the ELB and VPC.
    """
    def __init__(self, app):
        self.title = 'ELB not matching ports of security group.'
        self.description = (
            'The inbound rules of an Amazon VPC Security group associated with the load balancer '
            'allows access to ports that are not defined in the listener configuration of the loader.'
        )
        self.why_is_it_important = (
            'Having ports open unnecessarily can increase the risk of losing data or malicious attacks.'
        )
        self.how_do_i_fix_it = (
            'Change or remove the rules in the security group that refer to the ports '
            'that are undefined in the listener configuration.'
        )
        super(ELBSecurityGroupsYellow, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        pass


class ELBSecurityGroupsRed(ELBSecurityGroups):
    """
    Subclass checking for existance of a security group for the ELB.
    """
    def __init__(self, app):
        self.title = 'A security group associated with a load balancer does not exist.'
        self.description = (
            'A security group associated with a load balancer does not exist.'
        )
        self.why_is_it_important = (
            'If a security group associated with a load balancer is deleted, '
            'the load balancer does not work as expected.'
        )
        self.how_do_i_fix_it = (
            'Create a new security group and reconfigure the load balancer to refer to it.'
            'Please follow the AWS quidance on how to attach a security group to  a load balancer:'
            'https://aws.amazon.com/premiumsupport/knowledge-center/security-group-load-balancer/ '
        )
        super(ELBSecurityGroupsRed, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        pass
