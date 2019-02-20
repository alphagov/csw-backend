# AwsVpcFlowLogsEnabled
# Extends GdsEc2Client

from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_ec2_client import GdsEc2Client


class AwsVpcFlowLogsEnabled(CriteriaDefault):

    active = True

    is_regional = True

    ClientClass = GdsEc2Client

    resource_type = "AWS::EC2::VPC"

    title = "VPC Flow Logs: Flow logs enabled"

    description = "Checks whether Amazon Virtual Private Cloud flow logs are found and enabled for Amazon VPC."

    why_is_it_important = (
        "If flow logs are not enabled, it will be more difficult to analyse and monitor traffic into and out of your "
        "VPCs. This may increase the time it takes to detect and/or respond to a security event involving your VPC(s)."
    )

    how_do_i_fix_it = "Todo"  # TODO

    def get_data(self, session, **params):
        # use params to reference region - see audit.py
        pass

    def evaluate(self):
        pass
