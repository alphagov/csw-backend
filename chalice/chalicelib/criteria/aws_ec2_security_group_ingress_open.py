# GdsEc2Client
# extends GdsAwsClient
# implements aws ec2 api queries
from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_ec2_security_group_client import GdsEc2SecurityGroupClient


class AwsEc2SecurityGroupIngressOpen(CriteriaDefault):

    active = True

    ClientClass = GdsEc2SecurityGroupClient

    resource_type = "AWS::EC2::SecurityGroup"

    title = "EC2 Security Groups: Flagged port ingress is restricted"

    description = (
        "Checks that there are no security groups allowing inbound access from any address (IP/0) to a list of "
        "restricted ports including common database ports and FTP. Open access to the following ports is flagged: 20, "
        "21, 22, 1433, 1434, 3306, 3389, 4333, 5432, 5500."
    )
    why_is_it_important = """By opening ports like FTP or common database connection ports to the 
    world you dramatically increase the risk to your service"""

    how_do_i_fix_it = """Change unrestricted CIDR to an internal IP range or a whitelist of specific 
    IP addresses"""

    flag_unrestricted_ports = [20, 21, 1433, 1434, 3306, 3389, 4333, 5432, 5500]

    def get_data(self, session, **kwargs):
        return self.client.describe_security_groups(session, **kwargs)

    def translate(self, data):

        item = {"resource_id": data["GroupId"], "resource_name": data["GroupName"]}

        return item

    def get_port_list(self):

        string_ports = []
        for port in self.flag_unrestricted_ports:
            string_ports.append(str(port))

        return ", ".join(string_ports)

    def evaluate(self, event, item, whitelist=[]):

        self.app.log.debug("Evaluating compliance")
        self.annotation = ""

        has_relevant_rule = False
        is_compliant = True

        for ingress_rule in item["IpPermissions"]:

            self.app.log.debug("ingress rule")
            # self.app.log.debug(json.dumps(rule))

            if self.rule_applies_to_flagged_port(ingress_rule):

                self.app.log.debug(
                    "Port range applies to flagged port: "
                    + self.client.get_port_range(ingress_rule)
                )

                has_relevant_rule = True
                rule_is_compliant = self.rule_is_compliant(ingress_rule, whitelist)
                is_compliant &= rule_is_compliant

        if has_relevant_rule:
            if is_compliant:
                compliance_type = "COMPLIANT"
            else:
                compliance_type = "NON_COMPLIANT"
        else:
            compliance_type = "NOT_APPLICABLE"
            self.annotation = (
                "This group does not contain rules applying to flagged ports "
            )
            self.annotation += self.get_port_list()

        evaluation = self.build_evaluation(
            item["GroupId"], compliance_type, event, self.resource_type, self.annotation
        )

        # apply filter to mark default security groups as compliant by exception
        evaluation = self.client.except_default_security_groups(item, evaluation)

        return evaluation

    def rule_is_compliant(self, rule, whitelist):

        compliant = True

        for ip_range in rule["IpRanges"]:

            cidr_is_valid = True

            if "CidrIp" in ip_range:
                cidr = ip_range["CidrIp"]
                parsed_cidr = self.client.parse_v4_cidr(cidr)
                cidr_is_valid = parsed_cidr["mask"] != 0

            elif "CidrIpv6" in ip_range:
                cidr = ip_range["CidrIpv6"]
                parsed_cidr = self.client.parse_v6_cidr(cidr)
                cidr_is_valid = parsed_cidr["mask"] != 0

            compliant &= cidr_is_valid

            if not cidr_is_valid:
                add_note = (
                    f"The IP range {cidr} is not valid for port range: "
                    + self.client.get_port_range(rule)
                    + " "
                )
                self.annotation += add_note
                self.app.log.debug(add_note)

        return compliant

    def rule_applies_to_flagged_port(self, rule):

        is_protocol = self.client.is_protocol(rule, "tcp")

        in_port_range = False

        for port in self.flag_unrestricted_ports:

            flag_port_in_port_range = self.client.in_port_range(rule, port)

            if flag_port_in_port_range:
                in_port_range = True

            self.app.log.debug(
                "port: " + str(port) + " is flagged: " + str(flag_port_in_port_range)
            )

        self.app.log.debug("rule applies: " + str(in_port_range))

        rule["MatchesProtocol"] = is_protocol
        rule["MatchesPortRange"] = in_port_range

        return is_protocol and in_port_range
