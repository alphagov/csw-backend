# TODO - THIS HAS BEEN REPLACED BUT I'M HANGING ON TO THE CODE FOR NOW AS A REFERENCE FOR CALLING TRUSTED ADVISOR
# GdsSupportClient
# extends GdsAwsClient
# implements aws support endpoint queries for Trusted Advisor data


"""
{
    "result": {
        "checkId": "HCP4007jGY",
        "timestamp": "2018-09-10T14:14:16Z",
        "status": "warning",
        "resourcesSummary": {
            "resourcesProcessed": 49,
            "resourcesFlagged": 1,
            "resourcesIgnored": 0,
            "resourcesSuppressed": 0
        },
        "categorySpecificSummary": {
            "costOptimizing": {
                "estimatedMonthlySavings": 0.0,
                "estimatedPercentMonthlySavings": 0.0
            }
        },
        "flaggedResources": [
            {
                "status": "warning",
                "region": "--",
                "resourceId": "--",
                "isSuppressed": false,
                "metadata": [
                    "-- region --",
                    "-- name --",
                    "-- id -- (-- vpc --)",
                    "tcp",
                    "Yellow",
                    "8088"
                ]
            }
        ]
    }
}
"""

from chalicelib.aws.gds_support_client import GdsSupportClient


class GdsSupportEgressOpenClient(GdsSupportClient):
    def translate(self, data):

        item = {"resource_id": data["GroupId"], "resource_name": data["GroupName"]}

        return item

    def summarize(self, groups):

        summary = {
            "all": {"display_stat": 0, "category": "all", "modifier_class": "tested"},
            "applicable": {
                "display_stat": 0,
                "category": "tested",
                "modifier_class": "precheck",
            },
            "non_compliant": {
                "display_stat": 0,
                "category": "failed",
                "modifier_class": "failed",
            },
            "compliant": {
                "display_stat": 0,
                "category": "passed",
                "modifier_class": "passed",
            },
            "non_applicable": {
                "display_stat": 0,
                "category": "ignored",
                "modifier_class": "passed",
            },
        }

        for group in groups:

            group.resourceType = "AWS::EC2::SecurityGroup"

            compliance = group.resource_compliance

            self.app.log.debug("set resource type")

            summary["all"]["display_stat"] += 1

            if compliance.is_applicable:
                summary["applicable"]["display_stat"] += 1

                if compliance.is_compliant:
                    summary["compliant"]["display_stat"] += 1
                else:
                    summary["non_compliant"]["display_stat"] += 1

            else:
                summary["non_applicable"]["display_stat"] += 1

        return summary

    def evaluate(self, event, item, whitelist=[]):

        self.app.log.debug("Evaluating compliance")
        self.annotation = ""

        has_relevant_rule = False
        is_compliant = True

        for ingress_rule in item["IpPermissions"]:

            self.app.log.debug("ingress rule")
            # self.app.log.debug(json.dumps(rule))

            if self.rule_applies_to_ssh(ingress_rule):
                self.app.log.debug("Applies to SSH")
                has_relevant_rule = True
                rule_is_compliant = self.rule_is_compliant(ingress_rule, whitelist)
                is_compliant &= rule_is_compliant

        if has_relevant_rule:
            if is_compliant:
                compliance_type = "COMPLIANT"
            else:
                compliance_type = "NON_COMPLIANT"
        else:
            compliance_type = "NON_APPLICABLE"
            self.annotation = "This group does not contain rules applying to SSH"

        evaluation = self.build_evaluation(
            item["GroupId"], compliance_type, event, self.resource_type, self.annotation
        )

        return evaluation
