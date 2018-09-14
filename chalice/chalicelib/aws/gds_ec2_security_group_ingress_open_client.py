# GdsEc2Client
# extends GdsAwsClient
# implements aws ec2 api queries
from chalicelib.aws.gds_ec2_security_group_client import GdsEc2SecurityGroupClient


class GdsEc2SecurityGroupIngressOpenClient(GdsEc2SecurityGroupClient):

    '''
    Red: Access
    to
    port
    20, 21, 1433, 1434, 3306, 3389, 4333, 5432, or 5500 is unrestricted.

    -- only implement RED for now
    Yellow: Access
    to
    any
    other
    port is unrestricted.

    Green: Access
    to
    port
    80, 25, 443, or 465 is unrestricted.
    '''
    flag_unrestricted_ports = [
        20,
        21,
        1433,
        1434,
        3306,
        3389,
        4333,
        5432,
        5500
    ]

    def summarize(self, groups):

        summary = {
            'all': {
                'display_stat': 0,
                'category': 'all',
                'modifier_class': 'tested'
            },
            'applicable': {
                'display_stat': 0,
                'category': 'tested',
                'modifier_class': 'precheck'
            },
            'non_compliant': {
                'display_stat': 0,
                'category': 'failed',
                'modifier_class': 'failed'
            },
            'compliant': {
                'display_stat': 0,
                'category': 'passed',
                'modifier_class': 'passed'
            },
            'non_applicable': {
                'display_stat': 0,
                'category': 'ignored',
                'modifier_class': 'passed'
            }
        }

        for group in groups:

            group.resourceType = 'AWS::EC2::SecurityGroup'

            compliance = group.resource_compliance

            self.app.log.debug('set resource type')

            summary['all']['display_stat'] += 1

            if compliance.is_applicable:
                summary['applicable']['display_stat'] += 1

                if compliance.is_compliant:
                    summary['compliant']['display_stat'] += 1
                else:
                    summary['non_compliant']['display_stat'] += 1

            else:
                summary['non_applicable']['display_stat'] += 1

        return summary


    def evaluate(self, event, item, whitelist=[]):

        self.app.log.debug('Evaluating compliance')
        self.annotation = ""

        has_relevant_rule = False
        is_compliant = True

        for ingress_rule in item['IpPermissions']:

            self.app.log.debug('ingress rule')
            # self.app.log.debug(json.dumps(rule))

            if self.rule_applies_to_flagged_port(ingress_rule):

                self.app.log.debug("Port range applies to flagged port: " + self.get_port_range(ingress_rule))

                has_relevant_rule = True
                rule_is_compliant = self.rule_is_compliant(ingress_rule, whitelist)
                is_compliant &= rule_is_compliant

        if has_relevant_rule:
            if is_compliant:
                compliance_type = 'COMPLIANT'
            else:
                compliance_type = 'NON_COMPLIANT'
        else:
            compliance_type = 'NOT_APPLICABLE'
            self.annotation = "This group does not contain rules applying to flagged ports " \
                              + ", ".join(self.flag_unrestricted_ports)

        evaluation = self.build_evaluation(item['GroupId'], compliance_type, event, self.resource_type, self.annotation)

        return evaluation


    def rule_is_compliant(self, rule, whitelist):

        compliant = True

        for ip_range in rule['IpRanges']:

            cidr_is_valid = True

            if "CidrIp" in ip_range:
                cidr = ip_range["CidrIp"]
                cidr_is_valid = (cidr != "0.0.0.0/0")

            elif "CidrIpv6" in ip_range:
                cidr = ip_range["CidrIpv6"]
                cidr_is_valid = (cidr != "::/0")

            cidr_is_valid = cidr in whitelist
            compliant &= cidr_is_valid

            if not cidr_is_valid:
                add_note = f"The IP range {cidr} is not valid for port range: " + self.get_port_range(rule) + " "
                self.annotation += add_note
                self.app.log.debug(add_note)

        return compliant


    def rule_applies_to_flagged_port(self, rule):

        is_protocol = self.is_protocol(rule, 'tcp')

        in_port_range = False

        for port in self.flag_unrestricted_ports:

            flag_port_in_port_range = self.in_port_range(rule, port)

            if flag_port_in_port_range:
                in_port_range = True

        rule['MatchesProtocol'] = is_protocol
        rule['MatchesPortRange'] = in_port_range

        return is_protocol and in_port_range
