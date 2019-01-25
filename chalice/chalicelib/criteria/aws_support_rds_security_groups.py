"""
implements aws::rds::security_groups
checkId: nNauJisYIT
TA checks for unrestricted access to the amazon classic security groups
"""
from chalicelib.criteria.criteria_default import TrustedAdvisorCriterion


class AwsSupportRDSSecurityGroups(TrustedAdvisorCriterion):
    """
    Superclass for both checks.
    """
    def __init__(self, app):
        self.resource_type = 'AWS::RDS::SecurityGroups'
        self.check_id = 'nNauJisYIT'
        self.how_do_i_fix_it = (
            'This issue means that you are using the legacy EC2-Classic platform, and you do not have a default VPC. <br />'
            'To verify which DB instance you are running, please see '
            '<a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.FindDefaultVPC.html">this link</a>. <br /> '
            'If you want to move a DB instance which is not in a VPC, '
            'you can use the AWS Management Console to easily move your DB instance into a VPC, '
            'please refer to the '
            '<a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.html#USER_VPC.Non-VPC2VPC">'
            'AWS documentation</a>. <br />'
            'Moreover, consider reviewing the security group rules that grant global access to ensure the rules allow access '
            'from trusted IP addresses. For a list of GDS IPs, see '
            '<a href="https://sites.google.com/a/digital.cabinet-office.gov.uk/gds-internal-it/news/whitechapel-sourceipaddresses">this page</a>.'
            'See the AWS guidance on updating security groups: '
            '<a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-network-security.html#updating-security-group-rules">EC2</a>, '
            '<a href="https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html#AddRemoveRules">VPC</a>.'
        )
        super(AwsSupportRDSSecurityGroups, self).__init__(app)


class AwsSupportRDSSecurityGroupsYellow(AwsSupportRDSSecurityGroups):
    """
    Subclass checking for port mismatch between the ELB and VPC.
    """
    active = True

    def __init__(self, app):
        self.title = 'Amazon RDS Security Group Insufficient Access Restrictions'
        self.description = (
            'A rule in the database security group references an Amazon EC2 security group, '
            'which grants global access to a range of IP addresses or on a commonly used port '
            '(20, 21, 22, 1433, 1434, 3306, 3389, 4333, 5432, 5500).'
        )
        self.why_is_it_important = (
            'If these ports are globally accessible, '
            'then it may be possible that an unauthorized person can gain access to the database, '
            'and the potentially sensitive data contained inside.'
        )
        super(AwsSupportRDSSecurityGroupsYellow, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = 'COMPLIANT'
        if item["status"] == 'warning':
            compliance_type = 'NON_COMPLIANT'
            self.annotation = (
                f'The RDS security group "{item["metadata"][1]}"  in region "{item["metadata"][0]}" '
                'has very permissive access to IP ranges and/or ports.'
            )
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )


class AwsSupportRDSSecurityGroupsRed(AwsSupportRDSSecurityGroups):
    """
    Subclass checking for port mismatch between the ELB and VPC.
    """
    active = True

    def __init__(self, app):
        self.title = 'Amazon RDS Security Group Unrestricted Access'
        self.description = (
            'A rule in the database security group grants global access (i.e. access from any IP address).'
        )
        self.why_is_it_important = (
            'In general, there is no need for connections from outside AWS or GDS to connect directly to a database. <br />'
            'Allowing this opens up the possibility of the database being accessed, and possibly its contents read or even modified. <br />'
            'This is a very large risk that should not be taken.'
        )
        super(AwsSupportRDSSecurityGroupsRed, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = 'COMPLIANT'
        if item["status"] == 'error':
            compliance_type = 'NON_COMPLIANT'
            self.annotation = (
                f'The RDS security group "{item["metadata"][1]}"  in region "{item["metadata"][0]}" '
                'has unrestricted access to all IP ranges and ports.'
            )
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )
