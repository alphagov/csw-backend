"""
GdsKmsClient
extends GdsAwsClient
implements aws Key Management Service endpoint queries
"""
from chalicelib.aws.gds_aws_client import GdsAwsClient


class GdsElbClient(GdsAwsClient):
    """
    """

    def get_balancer_list_with_attributes(self, session):
        balancer_list = self.get_balancer_list(session)
        for balancer in balancer_list:
            for kv in self.get_balancer_attributes(session, balancer['LoadBalancerArn']):
                balancer.update({kv['Key']: kv['Value']})
        self.app.log.debug('ELB::get_balancer_list_with_attributes')
        self.app.log.debug(type(balancer_list))
        self.app.log.debug(balancer_list)
        return balancer_list

    def get_balancer_list(self, session):
        """
        """
        client = self.get_boto3_session_client('elbv2', session)
        return client.describe_load_balancers().get('LoadBalancers', [])

    def get_balancer_attributes(self, session, load_balancer_arn):
        """
        """
        client = self.get_boto3_session_client('elbv2', session)
        return client.describe_load_balancer_attributes(LoadBalancerArn=load_balancer_arn).get('Attributes', [])

