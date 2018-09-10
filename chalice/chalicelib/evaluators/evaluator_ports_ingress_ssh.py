import json
from chalicelib.evaluators.evaluator import Evaluator


class EvaluatorPortsIngressSsh(Evaluator):

    valid_ranges = [
        "213.86.153.212/32",
        "213.86.153.213/32",
        "213.86.153.214/32",
        "213.86.153.235/32",
        "213.86.153.236/32",
        "213.86.153.237/32",
        "85.133.67.244/32"
    ]
    annotation = ""

    def __init__(self, app):
        self.app = app
        self.default_resource_type = 'AWS::EC2::SecurityGroup'
        self.applicable_resources = ['AWS::EC2::SecurityGroup']

    def evaluate_compliance(self, event, item, valid_rule_parameters):

        self.app.log.debug('Evaluating compliance')
        annotation = None

        if item["resourceType"] not in self.applicable_resources:
            compliance_type = 'NON_APPLICABLE'
            annotation = f"This rule does not apply to the supplied resource { item['resourceName'] }"

        else:
            compliance_type = 'NON_COMPLIANT'
            has_relevant_rule = False
            is_compliant = True

            for ingress_rule in item['IpPermissions']:

                self.app.log.debug('ingress rule')
                # self.app.log.debug(json.dumps(rule))

                if self.rule_applies_to_ssh(ingress_rule):
                    self.app.log.debug('Applies to SSH')
                    has_relevant_rule = True
                    rule_is_compliant = self.rule_is_compliant(ingress_rule)
                    is_compliant &= rule_is_compliant

            if has_relevant_rule:
                if is_compliant:
                    compliance_type = 'COMPLIANT'
                else:
                    compliance_type = 'NON_COMPLIANT'
            else:
                compliance_type = 'NON_APPLICABLE'
                self.annotation = "This group does not contain rules applying to SSH"

        evaluation = self.build_evaluation(item['GroupId'], compliance_type, event, item["resourceType"], self.annotation)

        return evaluation

    def rule_is_compliant(self, rule):

        compliant = True

        for ip_range in rule['IpRanges']:

            cidr = ip_range["CidrIp"]
            cidr_is_valid = cidr in self.valid_ranges
            compliant &= cidr_is_valid

            if not cidr_is_valid:
                self.annotation += f"The IP range {cidr} is not valid. "

        return compliant

    def rule_applies_to_ssh(self, rule):

        is_protocol = self.is_protocol(rule, 'tcp')

        in_port_range = self.in_port_range(rule, 22)

        rule['MatchesProtocol'] = is_protocol
        rule['MatchesPortRange'] = in_port_range

        return is_protocol and in_port_range

    def is_protocol(self, rule, required_protocol):

        protocol = rule['IpProtocol']

        self.app.log.debug('protocol: ' + protocol)

        return protocol in [required_protocol,'-1']

    def in_port_range(self, rule, required_port):

        if ('FromPort' in rule):
            from_port = rule['FromPort']
            to_port = rule['ToPort']
            in_range = ((from_port <= required_port) and (to_port >= required_port))
        else:
            in_range = False

        return in_range

