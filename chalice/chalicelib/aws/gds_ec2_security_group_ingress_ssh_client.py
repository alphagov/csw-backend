# GdsEc2Client
# extends GdsAwsClient
# implements aws ec2 api queries
from chalicelib.aws.gds_ec2_security_group_client import GdsEc2SecurityGroupClient


class GdsEc2SecurityGroupIngressSshClient(GdsEc2SecurityGroupClient):

    valid_ranges = [
        "213.86.153.212/32",
        "213.86.153.213/32",
        "213.86.153.214/32",
        "213.86.153.235/32",
        "213.86.153.236/32",
        "213.86.153.237/32",
        "85.133.67.244/32",
        "10.0.0.0/8",
        "192.168.0.0/16"
    ]

    def evaluate(self, event, item, whitelist=[]):

        whitelist.extend(self.valid_ranges)

        self.app.log.debug('Evaluating compliance')
        self.annotation = ""

        has_relevant_rule = False
        is_compliant = True

        for ingress_rule in item['IpPermissions']:

            self.app.log.debug('ingress rule')
            # self.app.log.debug(json.dumps(rule))

            if self.rule_applies_to_ssh(ingress_rule):
                self.app.log.debug('Applies to SSH')
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
            self.annotation = "This group does not contain rules applying to SSH"

        evaluation = self.build_evaluation(item['GroupId'], compliance_type, event, self.resource_type, self.annotation)

        return evaluation


    def rule_is_compliant(self, rule, whitelist):

        compliant = True

        for ip_range in rule['IpRanges']:

            cidr = ip_range["CidrIp"]
            cidr_is_valid = cidr in whitelist
            compliant &= cidr_is_valid

            if not cidr_is_valid:
                self.annotation += f"The IP range {cidr} is not valid. "
                self.app.log.debug(f"The IP range {cidr} is not valid. ")

        return compliant


    def rule_applies_to_ssh(self, rule):

        is_protocol = self.is_protocol(rule, 'tcp')

        in_port_range = self.in_port_range(rule, 22)

        rule['MatchesProtocol'] = is_protocol
        rule['MatchesPortRange'] = in_port_range

        return is_protocol and in_port_range

