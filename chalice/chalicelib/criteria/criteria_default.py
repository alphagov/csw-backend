import json

from chalicelib.aws.gds_aws_client import GdsAwsClient
from chalicelib.aws.gds_support_client import GdsSupportClient


class CriteriaDefault():

    active = False

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

    def describe(self):
        return {
            "title": self.title,
            "description": self.description,
            "why_is_it_important": self.why_is_it_important,
            "how_do_i_fix_it": self.how_do_i_fix_it
        }

    def get_data(self, session, **kwargs):
        return []

    def build_evaluation(
        self, resource_id, compliance_type, event, resource_type,
        annotation=None
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
        eval = {}
        if annotation:
            eval['annotation'] = annotation
        eval['resource_type'] = resource_type
        eval['resource_id'] = resource_id
        eval['compliance_type'] = compliance_type
        eval['is_compliant'] = (compliance_type == 'COMPLIANT')
        eval['is_applicable'] = (compliance_type != 'NOT_APPLICABLE')
        eval['status_id'] = self.get_status(eval)

        return eval

    def get_status(self, eval):

        if eval["is_compliant"] or not eval["is_applicable"]:
            status = 2  # Pass

        elif not eval["is_compliant"]:
            status = 3  # Fail

        return status

    def empty_summary(self):

        return {
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
            'not_applicable': {
                'display_stat': 0,
                'category': 'ignored',
                'modifier_class': 'passed'
            },
            'regions': {
                'list': [],
                'count': 0
            }
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

            self.app.log.debug('set resource type')

            summary['all']['display_stat'] += 1

            if compliance["is_applicable"]:
                summary['applicable']['display_stat'] += 1

                if compliance["is_compliant"]:
                    summary['compliant']['display_stat'] += 1
                else:
                    summary['non_compliant']['display_stat'] += 1

            else:
                summary['not_applicable']['display_stat'] += 1

            summary["regions"]["list"] = regions
            summary["regions"]["count"] = len(regions)

        return summary


class TrustedAdvisorCriterion(CriteriaDefault):
    """
    A specialisation factoring out all the common attributes and methods
    of criteria that use one API call to describe TA in order to infer compliance.
    """
    def __init__(self, app):
        # attributes to overwrite in subclasses
        self.status_string = ''
        self.status_interval = ''
        # attributes common in both subclasses
        self.ClientClass = GdsSupportClient
        self.language = 'en'
        self.region = 'us-east-1'
        self.annotation = ''
        self.is_regional = False
        super(TrustedAdvisorCriterion, self).__init__(app)

    def get_data(self, session, **kwargs):
        output = self.client.describe_trusted_advisor_check_result(
            session,
            checkId=self.check_id,
            language=self.language
        )
        # if the TA results does not contain the key flaggedResources, add it with an empty list for its value
        if 'flaggedResources' not in output:
            output['flaggedResources'] = []
        self.app.log.debug(json.dumps(output))
        return output['flaggedResources']  # will have len() == 0 if compliant or non-applicable

    def translate(self, data={}):
        return {
            'resource_id': data.get('resourceId', ''),
            'resource_name': data.get('metadata', ['', '', ])[1],  # trail name or empty string
        }
