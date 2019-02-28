# AwsVpcFlowLogsEnabled
# Extends GdsEc2Client
# Checks every VPC in current region to see if flow logs exist for those VPCs

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
        "<a href=\"https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-cwl.html#flow-logs-cwl-create-flow-log\">"
        "https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-cwl.html#flow-logs-cwl-create-flow-log</a><br />"
        "Publishing Flow Logs to Amazon S3: "
        "<a href=\"https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-s3.html#flow-logs-s3-create-flow-log\">"
        "https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-s3.html#flow-logs-s3-create-flow-log</a>"
    )

    def get_data(self, session, **params):

        self.app.log.debug(f"Getting VPCs from region {params['region']}")
        vpcs = self.client.describe_vpcs(session, params["region"])

        self.app.log.debug("Got VPCs, iterating over them to get flow log data")
        for vpc in vpcs:
            vpc["FlowLog"] = self.client.describe_flow_logs(session, vpc, params["region"])

        self.app.log.debug("Got all the flow log data")
        return vpcs

    def translate(self, data):

        # Finding the name of this VPC, if it has one
        if "Tags" in data:
            for tag in data["Tags"]:
                if tag["Key"] == "Name":
                    name = tag["Value"]
                    break
            else:  # No Name tag found
                name = ""
        else:
            name = ""

        item = {
            "resource_id": data.get("VpcId", ""),
            "resource_name": name
        }
        return item

    def evaluate(self, event, vpc, whitelist=[]):
        if len(vpc["FlowLog"]) == 0:  # No flow log
            compliance_type = "NOT_COMPLIANT"
            self.annotation = "VPC does not have a flow log set up."
            log_string = "VPC does not have a flow log"
        else:  # If the FlowLog key has anything in it, it means that the flow log exists
            compliance_type = "COMPLIANT"
            log_string = "VPC has a flow log"

        evaluation = self.build_evaluation(
            vpc["VpcId"],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )

        self.app.log.debug(log_string)
        return evaluation
