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
    resource_type = "AWS::ELB::LOGGING"
    title = "ELB: Logging Enabled"
    description = "Access logs have not been enabled for this load balancer."
    why_is_it_important = (
        "Elastic Load Balancing (ELB) provides access logs "
        "that capture detailed information about requests sent to your load balancer. "
        "Each log contains information such as the time the request was received, "
        "the client's IP address, latencies, request paths, and server responses. "
        "You can use these access logs to analyze traffic patterns and troubleshoot issues, "
        "such as security incidents."
    )
    how_do_i_fix_it = (
        'This <a href="https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/enable-access-logs.html">'
        "AWS documentation</a> explains how to enable access logs for your load balancer."
    )

    def get_data(self, session, **kwargs):
        return self.client.get_balancer_list_with_attributes(session)

    def translate(self, data={}):
        return {
            "region": data["LoadBalancerArn"].split(":")[3],
            "resource_id": data["LoadBalancerArn"],
            "resource_name": data["LoadBalancerName"],
        }

    def evaluate(self, event, item, whitelist=[]):
        if item["access_logs.s3.enabled"] == "true":
            compliance_type = "COMPLIANT"
            self.annotation = ""
        else:
            compliance_type = "NON_COMPLIANT"
            self.annotation = (
                "This load balancer is not sending its logs to any S3 bucket."
            )
        return self.build_evaluation(
            item["LoadBalancerArn"],
            compliance_type,
            event,
            self.resource_type,
            self.annotation,
        )
