"""
implements aws::elb::security_groups
checkId: xSqX82fQu
TA checks for load balancers belonging to a security group.
"""
from chalicelib.criteria.criteria_default import TrustedAdvisorCriterion


class ELBSecurityGroups(TrustedAdvisorCriterion):
    """
    Superclass for both checks.
    """

    def __init__(self, app):
        self.resource_type = "AWS::ELB::SecurityGroups"
        self.check_id = "xSqX82fQu"
        super(ELBSecurityGroups, self).__init__(app)


class ELBSecurityGroupsYellow(ELBSecurityGroups):
    """
    Subclass checking for port mismatch between the ELB and VPC.
    """

    active = True
    severity = 3

    def __init__(self, app):
        self.title = "ELB Security Groups: Ingress ports match listener configuration"
        self.description = (
            "Checks that the inbound rules of the Security Group associated with a Load Balancer does not allow access "
            "to ports that are not defined in the Load Balancer listener configuration."
        )
        self.why_is_it_important = "Having ports open unnecessarily can increase the risk of losing data or malicious attacks."
        self.how_do_i_fix_it = (
            "Change or remove the rules in the security group that refer to the ports "
            "that are undefined in the listener configuration."
        )
        super(ELBSecurityGroupsYellow, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = "COMPLIANT"
        # Remove any previous annotation if instance is reused
        self.annotation = ""

        if item["metadata"][2] == "Yellow":
            compliance_type = "NON_COMPLIANT"
            self.annotation = (
                f'The security group (with ID "{item["metadata"][3]}") allows access to ports that '
                f'are not configured for the load balancer "{item["metadata"][1]}" in region "{item["metadata"][0]}".'
            )
        return self.build_evaluation(
            item["resourceId"],
            compliance_type,
            event,
            self.resource_type,
            self.annotation,
        )


class ELBSecurityGroupsRed(ELBSecurityGroups):
    """
    Subclass checking for existance of a security group for the ELB.
    """

    active = True
    severity = 3

    def __init__(self, app):
        self.title = "ELB Security Groups: The load balancer security group exists"
        self.description = "Checks that there is a Security Group associated with a Load Balancer and that the Security Group exists."
        self.why_is_it_important = (
            "If a security group associated with a load balancer is deleted, "
            "the load balancer does not work as expected."
        )
        self.how_do_i_fix_it = (
            "Create a new security group and reconfigure the load balancer to refer to it."
            "Please follow the AWS quidance on "
            '<a href="https://aws.amazon.com/premiumsupport/knowledge-center/security-group-load-balancer/">how to attach a security group to a load balancer</a>.'
        )
        super(ELBSecurityGroupsRed, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = "COMPLIANT"
        if item["metadata"][2] == "Red":
            compliance_type = "NON_COMPLIANT"
            self.annotation = (
                "No security group associated with "
                f'the load balancer "{item["metadata"][1]}" in region "{item["metadata"][0]}".'
            )
        return self.build_evaluation(
            item["resourceId"],
            compliance_type,
            event,
            self.resource_type,
            self.annotation,
        )
