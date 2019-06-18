"""
"""
from chalicelib.aws.gds_cloudtrail_client import GdsCloudtrailClient
from chalicelib.criteria.criteria_default import CriteriaDefault


class MultiregionalCloudtrail(CriteriaDefault):
    """
    """

    active = True
    ClientClass = GdsCloudtrailClient
    is_regional = False
    resource_type = "AWS::CLOUDTRAIL:MULTIREGIONAL"
    title = "Cloud Trail: Multi-regional"
    description = "CloudTrail logs are not enabled for all AWS regions."
    why_is_it_important = (
        "Enabling global monitoring for at least one of your existing trails will help you "
        "to better manage your AWS account and maintain the security of your infrastructure. <br />"
        "For instance, a multi-region CloudTrail enabled, "
        "it is useful to record API calls in regions that are not used to detect any unusual activity."
    )
    how_do_i_fix_it = (
        "Ensure that CloudTrail is enabled for all AWS regions in order to "
        "increase the visibility of the API activity in your AWS account for security and management purposes. "
        "To receive CloudTrail log files from multiple regions, please see the "
        '<a href="https://docs.aws.amazon.com/awscloudtrail/latest/userguide/receive-cloudtrail-log-files-from-multiple-regions.html">AWS documentation</a>.'
    )

    def get_data(self, session, **kwargs):
        try:
            return self.client.describe_trails(session)
        except Exception:
            self.app.log.error(self.app.utilities.get_typed_exception())
            return []

    def translate(self, data={}):
        return {
            "region": data["HomeRegion"],
            "resource_id": data["TrailARN"],
            "resource_name": data["Name"],
        }

    def evaluate(self, event, item, whitelist=[]):
        if item["IsMultiRegionTrail"] == True:
            compliance_type = "COMPLIANT"
            self.annotation = ""
        else:
            compliance_type = "NON_COMPLIANT"
            self.annotation = f'The Trail "{item["Name"]}" in region "{item["HomeRegion"]}" is not multi-regional.'
        return self.build_evaluation(
            item["TrailARN"],
            compliance_type,
            event,
            self.resource_type,
            self.annotation,
        )
