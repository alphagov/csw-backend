import json
from datetime import datetime

from chalicelib.aws.gds_aws_client import GdsAwsClient
from chalicelib.aws.gds_support_client import GdsSupportClient


class CriteriaDefault:

    active = False
    severity = 1

    is_regional = True

    """
    exception_type = "resource" | "allowlist" 
    You can either record exceptions on a per resource basis 
    - This resource should be excluded from this check 
        "this load balancer does not accept web traffic"
    .. or on an allow-list basis 
    - This resource should not fail for this reason 
        "allowed ingress from a specified IP"
    """
    exception_type = "resource"

    """
    aggregation_type = "all" | "any"
    All (default) means that all resources have to pass for the check to pass
    and failed resources are recorded as part of the audit results

    Any means that if any individual resource passes then the check passes
    and individual failed resources are not recorded as part of the audit results
    """
    aggregation_type = "all"

    # Set default account_subscription_id which should be set in the
    # audit lambda by calling the set_account_subscription_id() method
    account_subscription_id = None

    resources = dict()

    resource_type = "AWS::*::*"
    annotation = ""

    ClientClass = GdsAwsClient

    title = None
    description = None
    why_is_it_important = None
    how_do_i_fix_it = None

    def __init__(self, app):
        self.app = app
        self.client = self.ClientClass(app)

    def get_session(self, account="default", role=""):
        return self.client.get_session(account, role)

    def get_chained_session(self, target_account):
        return self.client.get_chained_session(target_account)

    def get_aggregation_type(self):
        return self.aggregation_type

    def describe(self):
        return {
            "title": self.title,
            "description": self.description,
            "why_is_it_important": self.why_is_it_important,
            "how_do_i_fix_it": self.how_do_i_fix_it,
        }

    def get_data(self, session, **kwargs):
        return []

    def get_resource_persistent_id(self, item, audit):
        """
        The resource_identifier needs to be something which will
        be unchanged by a terraform destroy/apply so should not
        include the resource's ID.
        This is why the resource ARN is not the default.
        For IAM Users, Roles or S3 buckets the ARN can be used since
        the ARN contains the name and not an ID.

        By default the resource identifier is in the format:
        {criteria resource type}::{region}::{account}::{resource_name}

        This should be overridden for specific resource types
        where the default behaviour is not appropriate.
        :param item:
        :return:
        """

        # aim to use the resource name but fall back to the id if not defined
        if "resource_name" in item and item["resource_name"] is not None:
            name = item.get("resource_name", "")
        else:
            name = item.get("resource_id", "")

        return (
            self.resource_type
            + "::"
            + item.get("region", "")
            + "::"
            + str(audit.account_subscription_id.account_id)
            + "::"
            + name
        )

    def build_evaluation(
        self, resource_id, compliance_type, event, resource_type, annotation=None
    ):
        """
        Form an evaluation as a dictionary.
        Usually suited to report on scheduled rules.
        Keyword arguments:
        resource_id -- the unique id of the resource to report
        compliance_type -- either COMPLIANT, NON_COMPLIANT or NOT_APPLICABLE
        event -- the event variable given in the lambda handler
        resource_type -- the CloudFormation resource type (or AWS::::Account)
        to report on the rule (default DEFAULT_RESOURCE_TYPE)
        annotation -- an annotation to be added to the evaluation (def = None)
        """
        evaluation = {}
        if annotation:
            evaluation["annotation"] = annotation
        evaluation["resource_type"] = resource_type
        evaluation["resource_id"] = resource_id
        evaluation["compliance_type"] = compliance_type
        evaluation["is_compliant"] = compliance_type == "COMPLIANT"
        evaluation["is_applicable"] = compliance_type != "NOT_APPLICABLE"
        evaluation["status_id"] = self.get_status(evaluation)

        return evaluation

    def get_status(self, eval):

        if eval["is_compliant"] or not eval["is_applicable"]:
            status = 2  # Pass

        elif not eval["is_compliant"]:
            status = 3  # Fail

        return status

    def empty_summary(self):

        return {
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
            "not_applicable": {
                "display_stat": 0,
                "category": "ignored",
                "modifier_class": "passed",
            },
            "regions": {"list": [], "count": 0},
        }

    def summarize(self, resources, summary=None):

        regions = []

        if summary is None:
            summary = self.empty_summary()

        for resource in resources:

            has_region = "region" in resource
            is_default = resource["resource_name"] == "default"
            in_regions = has_region and resource["region"] in regions

            if has_region and (not is_default) and (not in_regions):
                regions.append(resource["region"])

            compliance = resource["resource_compliance"]

            self.app.log.debug(
                "summarize resource compliance: {}".format(
                    self.app.utilities.to_json(compliance)
                )
            )

            self.app.log.debug("set resource type")

            summary["all"]["display_stat"] += 1

            if compliance["is_applicable"]:
                summary["applicable"]["display_stat"] += 1

                if compliance["is_compliant"]:
                    summary["compliant"]["display_stat"] += 1
                else:
                    summary["non_compliant"]["display_stat"] += 1

            else:
                summary["not_applicable"]["display_stat"] += 1

            summary["regions"]["list"] = regions
            summary["regions"]["count"] = len(regions)

        return summary

    def translate(self, data={}):
        """
        Default method to create name and id fields for an audit_resource
        This method should be overridden for each AWS resource type to return
        approprate fields.
        :param data:
        :return:
        """
        item = {
            "resource_id": data.get("ResourceId", ""),
            "resource_name": data.get("Name", ""),  # trail name or empty string
        }
        return item

    def build_audit_resource_item(self, api_item, audit, criterion, params):

        item = self.translate(api_item)
        # store original API resource data
        item["resource_data"] = self.app.utilities.to_json(api_item)

        # populate foreign keys
        item["account_audit_id"] = audit
        item["criterion_id"] = criterion

        # set evaluated date
        item["date_evaluated"] = datetime.now()

        # for some TA checks the region will be populated from the
        # check.translate method.
        # for custom checks where an API call is made for each region
        # the region is added here.
        if "region" in params:
            item["region"] = params["region"]
            # item_raw["region"] = params["region"]

        # populate the resource_identifier field
        item["resource_persistent_id"] = self.get_resource_persistent_id(item, audit)

        return item

    def set_account_subscription_id(self, account_subscription_id):
        self.account_subscription_id = account_subscription_id


class TrustedAdvisorCriterion(CriteriaDefault):
    """
    A specialisation factoring out all the common attributes and methods
    of criteria that use one API call to describe TA in order to infer compliance.
    """
    ResourceClientClass = GdsAwsClient
    check_id = ""

    def __init__(self, app):
        # attributes to overwrite in subclasses
        self.status_string = ""
        self.status_interval = ""
        # attributes common in both subclasses
        self.ClientClass = GdsSupportClient
        self.language = "en"
        self.region = "us-east-1"
        self.annotation = ""
        self.is_regional = False
        super(TrustedAdvisorCriterion, self).__init__(app)
        self.resource_client = self.ResourceClientClass(app)

    def get_data(self, session, **kwargs):
        updated = self.client.refresh_check_with_wait(session, self.check_id)

        output = self.client.describe_trusted_advisor_check_result(
            session, checkId=self.check_id, language=self.language
        )
        # if the TA results does not contain the key flaggedResources, add it with an empty list for its value
        flagged = output.get("flaggedResources",[])
        for resource in flagged:
            region = resource["metadata"][0]
            original = self.get_resource_data(session, region, resource)
            resource["originalResourceData"] = original

        self.app.log.debug(json.dumps(output))
        return flagged  # will have len() == 0 if compliant or non-applicable

    def translate(self, data={}):
        """
        Default method to create name and id fields for an audit_resource
        from Trusted Advisor response - flagged_resources
        This method should be overridden for each AWS resource type to return
        approprate fields.
        :param data:
        :return:
        """

        item = {
            "resource_id": data.get("resourceId", ""),
            # trail name or empty string
            "resource_name": data.get("metadata", ["", ""])[1]
        }
        return item

    def get_resource_data(self, session, region, flagged_resource):
        return None
