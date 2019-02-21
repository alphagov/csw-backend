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

    how_do_i_fix_it = (
        "Enable flow logs in your VPCs. Flow logs can publish flow log data to Amazon S3 or to CloudWatch logs. "
        "Depends on your choice, see the following AWS documentation: <br />"
        "Publishing Flow Logs to CloudWatch Logs: "
        "https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-cwl.html#flow-logs-cwl-create-flow-log <br />"
        "Publishing Flow Logs to Amazon S3: "
        "https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-s3.html#flow-logs-s3-create-flow-log"
    )

    def get_data(self, session, **params):

        vpcs = self.client.describe_vpcs(session, params["region"])

        for vpc in vpcs:
            vpc["FlowLog"] = self.client.describe_flow_logs(session, vpc, params["region"])

        return vpcs

    def evaluate(self):
        pass
