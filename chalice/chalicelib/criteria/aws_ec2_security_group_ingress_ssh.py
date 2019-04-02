# GdsEc2Client
# extends GdsAwsClient
# implements aws ec2 api queries
import datetime
from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_ec2_security_group_client import GdsEc2SecurityGroupClient
from chalicelib.models import AccountSshCidrAllowlist


class AwsEc2SecurityGroupIngressSsh(CriteriaDefault):

    active = True
    severity = 3

    ClientClass = GdsEc2SecurityGroupClient
    AllowlistClass = AccountSshCidrAllowlist

    resource_type = "AWS::EC2::SecurityGroup"

    title = "EC2 Security Groups: SSH ingress is restricted to authorised IPs or CIDRs"

    exception_type = "allowlist"
    # exception_type = "resource"

    description = (
        "Checks that there are no security groups allowing inbound SSH access from any address or from specified "
        "addresses outside the GDS domain."
    )

    why_is_it_important = """If someone has access to either one of our WiFis or our 
    VPN then there is more chance they should have access"""

    how_do_i_fix_it = """In almost all cases, SSH ingress should be limited to the 
    <a target="gds-wiki" href="https://sites.google.com/a/digital.cabinet-office.gov.uk/gds-internal-it/news/aviationhouse-sourceipaddresses">GDS public IPs</a>. 
    There may be exceptions where we are working closely in partnership with another organisation."""

    valid_ranges = [
        "213.86.153.212/32",
        "213.86.153.213/32",
        "213.86.153.214/32",
        "213.86.153.235/32",
        "213.86.153.236/32",
        "213.86.153.237/32",
        "85.133.67.244/32"
    ]

    def get_data(self, session, **kwargs):
        return self.client.describe_security_groups(session, **kwargs)

    def translate(self, data):

        item = {
            "resource_id": data['GroupId'],
            "resource_name": data['GroupName'],
        }

        return item

    def evaluate(self, event, item, whitelist=[]):

        self.app.log.debug("Evaluating compliance")
        self.annotation = ""

        has_relevant_rule = False
        is_compliant = True
        if "IpPermissions" in item:
            for ingress_rule in item["IpPermissions"]:

                self.app.log.debug("ingress rule")
                # self.app.log.debug(json.dumps(rule))

                if self.rule_applies_to_ssh(ingress_rule):
                    self.app.log.debug("Applies to SSH")
                    has_relevant_rule = True
                    rule_is_compliant = self.rule_is_compliant(ingress_rule)
                    is_compliant &= rule_is_compliant

        if has_relevant_rule:
            if is_compliant:
                compliance_type = "COMPLIANT"
            else:
                compliance_type = "NON_COMPLIANT"
        else:
            compliance_type = "NOT_APPLICABLE"
            self.annotation = "This group does not contain rules applying to SSH"

        evaluation = self.build_evaluation(
            item["GroupId"], compliance_type, event, self.resource_type, self.annotation
        )

        # apply filter to mark default security groups as compliant by exception
        evaluation = self.client.except_default_security_groups(item, evaluation)

        return evaluation

    def get_valid_ranges(self):
        """
        Wrapper method: In chalice mode the allow list exceptions are stored in the database
        In CLI mode they are stored in a local JSON file
        """
        if self.app.mode == 'chalice' and self.account_subscription_id is not None:
            valid_ranges = self.get_chalice_valid_ranges()
        elif self.app.mode == 'cli':
            valid_ranges = self.get_cli_valid_ranges()
        return valid_ranges

    def get_chalice_valid_ranges(self):
        """
        Append the standard valid ranges with any custom exceptions from the databases
        """
        valid_ranges = self.valid_ranges.copy()
        now = datetime.datetime.now()
        # If the account ID is set retrieve any
        # allow list rules from the database
        # and append to valid_ranges
        allow_list = (AccountSshCidrAllowlist
            .select()
            .where(
            AccountSshCidrAllowlist.account_subscription_id == self.account_subscription_id,
            AccountSshCidrAllowlist.date_expires > now
        ))
        for item in allow_list:
            valid_ranges.append(item.cidr)
        return valid_ranges

    def get_cli_valid_ranges(self):
        try:
            valid_ranges = self.valid_ranges.copy()
            now = datetime.datetime.now()
            allowlist_json = self.app.utilities.read_file("config/allowlist.json")
            allowlist = self.app.utilities.from_json(allowlist_json)
            if allowlist is not None:
                for entry in allowlist:
                    expires = self.app.utilities.parse_datetime(entry["date_expires"])
                    if expires > now and self.app.audit["account"] == entry["account"]:
                        valid_ranges.append(entry["cidr"])
        except Exception as err:
            # The JSON file is git ignored so if there are no exceptions then there
            # will most likely not be a JSON file to read
            self.app.log.error("Allowlist error: "+ self.app.utilities.get_typed_exception(err))

        return valid_ranges

    def rule_is_compliant(self, rule):

        compliant = True

        annotations = []

        for ip_range in rule["IpRanges"]:

            cidr = ip_range["CidrIp"]

            valid_ranges = self.get_valid_ranges()

            cidr_is_valid = False

            if cidr in valid_ranges:
                # check for exact cidr match first since it's simpler
                cidr_is_valid = True

            elif self.client.cidr_is_private_network(cidr):
                # also check for internal network first since it's simpler
                cidr_is_valid = True
            else:
                # perform proper cidr comparisons
                for valid_cidr in valid_ranges:
                    if self.client.parent_cidr_contains_child_cidr(valid_cidr, cidr):
                        # check whether cidr is contained by any of the valid cidrs
                        cidr_is_valid = True
                        break
                    elif self.client.cidrs_equivalent(valid_cidr, cidr):
                        # also check equivalent cidrs
                        # eg 10.4.3.0/16 is equivalent to 10.4.255.0/16
                        # since only the first 16 bits (10.4) are matched.
                        # by convention these should be written as 10.4.0.0/16
                        # but this may not always be the case
                        cidr_is_valid = True
                        break

            compliant &= cidr_is_valid

            if not cidr_is_valid:
                annotations.append(f"The IP range {cidr} is not valid. ")
                self.app.log.debug(f"The IP range {cidr} is not valid. ")

            if len(annotations) > 0:
                self.annotation = "<br/>".join(annotations)

        return compliant

    def rule_applies_to_ssh(self, rule):

        is_protocol = self.client.is_protocol(rule, "tcp")

        in_port_range = self.client.in_port_range(rule, 22)

        rule["MatchesProtocol"] = is_protocol
        rule["MatchesPortRange"] = in_port_range

        return is_protocol and in_port_range
