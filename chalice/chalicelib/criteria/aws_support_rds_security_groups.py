"""
implements aws::rds::security_groups
checkId: nNauJisYIT
TA checks for unrestricted access to the amazon classic security groups
"""
from chalicelib.criteria.criteria_default import TrustedAdvisorCriterion
from chalicelib.aws.gds_ec2_security_group_client import GdsEc2SecurityGroupClient


class AwsSupportRDSSecurityGroups(TrustedAdvisorCriterion):
    """
    Superclass for both checks.
    """
    ResourceClientClass = GdsEc2SecurityGroupClient

    def __init__(self, app):
        self.resource_type = "AWS::RDS::SecurityGroups"
        self.check_id = "nNauJisYIT"
        self.how_do_i_fix_it = (
            "This issue means that you are using the legacy EC2-Classic platform, and you do not have a default VPC. <br />"
            "To verify which DB instance you are running, please see "
            '<a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.FindDefaultVPC.html">this link</a>. <br /> '
            "If you want to move a DB instance which is not in a VPC, "
            "you can use the AWS Management Console to easily move your DB instance into a VPC, "
            "please refer to the "
            '<a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.html#USER_VPC.Non-VPC2VPC">'
            "AWS documentation</a>. <br />"
            "Moreover, consider reviewing the security group rules that grant global access to ensure the rules allow access "
            "from trusted IP addresses. For a list of GDS IPs, see "
            '<a href="https://sites.google.com/a/digital.cabinet-office.gov.uk/gds-internal-it/news/whitechapel-sourceipaddresses">this page</a>.'
            "See the AWS guidance on updating security groups: "
            '<a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-network-security.html#updating-security-group-rules">EC2</a>, '
            '<a href="https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html#AddRemoveRules">VPC</a>.'
        )
        super(AwsSupportRDSSecurityGroups, self).__init__(app)

    def get_resource_data(self, session, region, resource):
        id = resource.get("resourceId",None)
        group = self.resource_client.get_security_group_by_id(session, region, id)
        return group


class AwsSupportRDSSecurityGroupsYellow(AwsSupportRDSSecurityGroups):
    """
    Subclass checking for port mismatch between the ELB and VPC.
    """

    active = True

    def __init__(self, app):
        self.title = "RDS Security Groups: Ingress is restricted for flagged ports"
        self.description = (
            "Checks that there are no Security Groups associated with RDS Instances allowing inbound access from any "
            "address (IP/0) to a list of restricted ports including common database ports and FTP. Open access to the "
            "following ports is flagged: 20, 21, 22, 1433, 1434, 3306, 3389, 4333, 5432, 5500."
        )
        self.why_is_it_important = (
            "If these ports are globally accessible, "
            "then it may be possible that an unauthorized person can gain access to the database, "
            "and the potentially sensitive data contained inside."
        )
        super(AwsSupportRDSSecurityGroupsYellow, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = "COMPLIANT"
        # Remove any previous annotation if instance is reused
        self.annotation = ""

        if item["status"] == "warning":
            compliance_type = "NON_COMPLIANT"
            self.annotation = (
                f'The RDS security group "{item["metadata"][1]}"  in region "{item["metadata"][0]}" '
                "has very permissive access to IP ranges and/or ports."
            )
        return self.build_evaluation(
            item["resourceId"],
            compliance_type,
            event,
            self.resource_type,
            self.annotation,
        )


class AwsSupportRDSSecurityGroupsRed(AwsSupportRDSSecurityGroups):
    """
    Subclass checking for port mismatch between the ELB and VPC.
    """

    active = True

    def __init__(self, app):
        self.title = (
            "RDS Security Groups: Ingress is restricted to specific IPs or CIDRs"
        )
        self.description = (
            "Checks that Security Groups associated with RDS instances limit inbound access rather than accepting "
            "connections from any IP address."
        )
        self.why_is_it_important = (
            "Limiting access to your database from known networks or through SSM sessions or bastion hosts limits "
            "adds an additional level of protection on top of the built-in authentication. Leaving ports open to "
            "the world makes vulnerabilities more exploitable."
        )
        super(AwsSupportRDSSecurityGroupsRed, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = "COMPLIANT"
        if item["status"] == "error":
            compliance_type = "NON_COMPLIANT"
            annotation = "Change the security group rules to remove any /0 CIDRS allowing global access. "

            resource = item.get("originalResourceData", None)
            if resource:
                rules = self.get_failed_rules(resource)
                for rule in rules:
                    annotation += f"<br/>CIDR {rule.cidr} is open to ports: {rule.ports}"

            self.annotation = annotation

        return self.build_evaluation(
            item["resourceId"],
            compliance_type,
            event,
            self.resource_type,
            self.annotation,
        )

    def get_failed_rules(self, resource):

        rules = []

        for rule in resource["IpPermissions"]:
            for ip_range in rule["IpRanges"]:

                if "CidrIp" in ip_range:
                    cidr = ip_range["CidrIp"]
                    parsed_cidr = self.client.parse_v4_cidr(cidr)
                    if parsed_cidr["mask"] == 0:
                        rules.append({
                            "ports": self.resource_client.get_port_range(rule),
                            "cidr": cidr
                        })

        return rules