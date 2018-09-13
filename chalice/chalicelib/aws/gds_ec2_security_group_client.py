# GdsEc2Client
# extends GdsAwsClient
# implements aws ec2 api queries
from chalicelib.aws.gds_ec2_client import GdsEc2Client


class GdsEc2SecurityGroupClient(GdsEc2Client):

    resource_type = "AWS::EC2::SecurityGroup"
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

    def describe_security_groups(self, session, **kwargs):

        # get a boto3 client for the EC2 service in the given region (default to London)
        ec2 = self.get_boto3_session_client('ec2', session, kwargs["region"])

        #if hasattr(self,'app'):
        #    self.app.log.debug('got session client')

        # run describe security groups api call
        response = ec2.describe_security_groups()

        #if hasattr(self, 'app'):
        #    self.app.log.debug('got response: ' + str(response))

        # return the security groups element of the response
        security_groups = response['SecurityGroups']

        return security_groups

    def translate(self, data):

        item = {
            "resource_id": data['GroupId'],
            "resource_name": data['GroupName'],
        }

        return item


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

            group['resourceType'] = 'AWS::EC2::SecurityGroup'

            self.app.log.debug('set resource type')

            compliance = self.evaluate_compliance({}, group, self.valid_ranges)

            summary['all']['display_stat'] += 1

            if compliance['IsApplicable']:
                summary['applicable']['display_stat'] += 1

                if compliance['IsCompliant']:
                    summary['compliant']['display_stat'] += 1
                else:
                    summary['non_compliant']['display_stat'] += 1

            else:
                summary['non_applicable']['display_stat'] += 1

            group['compliance'] = compliance

            self.app.log.debug(str(compliance))

        return summary, groups


    def evaluate(self, event, item, whitelist=[]):

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
            compliance_type = 'NON_APPLICABLE'
            self.annotation = "This group does not contain rules applying to SSH"

        evaluation = self.build_evaluation(item['GroupId'], compliance_type, event, item["resourceType"], self.annotation)

        return evaluation


    def rule_is_compliant(self, rule, whitelist):

        compliant = True

        for ip_range in rule['IpRanges']:

            cidr = ip_range["CidrIp"]
            cidr_is_valid = cidr in whitelist
            compliant &= cidr_is_valid

            if not cidr_is_valid:
                self.annotation += f"The IP range {cidr} is not valid."
                self.app.log.debug(f"The IP range {cidr} is not valid.")

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
