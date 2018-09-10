import json

class Evaluator:

    default_resource_type = None
    applicable_resources = []

    def __init__(self, app):
        self.app = app

    def evaluate_compliance(self, event, configuration_item, valid_rule_parameters):

        if configuration_item["resourceType"] not in self.applicable_resources:
            evaluation = 'NON_APPLICABLE'
        else:
            evaluation = self.build_evaluation(configuration_item['arn'], 'NON_COMPLIANT', event, None)

        return evaluation

    # This generate an evaluation for config
    def build_evaluation(self, resource_id, compliance_type, event, resource_type, annotation=None):

        """Form an evaluation as a dictionary. Usually suited to report on scheduled rules.
        Keyword arguments:
        resource_id -- the unique id of the resource to report
        compliance_type -- either COMPLIANT, NON_COMPLIANT or NOT_APPLICABLE
        event -- the event variable given in the lambda handler
        resource_type -- the CloudFormation resource type (or AWS::::Account) to report on the rule (default DEFAULT_RESOURCE_TYPE)
        annotation -- an annotation to be added to the evaluation (default None)
        """
        eval_cc = {}
        if annotation:
            eval_cc['Annotation'] = annotation
        eval_cc['ComplianceResourceType'] = resource_type
        eval_cc['ComplianceResourceId'] = resource_id
        eval_cc['ComplianceType'] = compliance_type
        eval_cc['IsCompliant'] = compliance_type == 'COMPLIANT'
        eval_cc['IsApplicable'] = compliance_type != 'NON_APPLICABLE'
        return eval_cc