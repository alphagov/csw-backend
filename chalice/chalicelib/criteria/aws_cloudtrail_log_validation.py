#Path file: /Users/sergionavarrovalverde/csw-backend/chalice/chalicelib/criteria/aws_cloudtrail_log_validation.py

from chalicelib.aws.gds_cloudtrail_client import GdsCloudtrailClient
from chalicelib.criteria.criteria_default import CriteriaDefault


class CloudTrailFileValidation(CriteriaDefault):
    """
    """
    active = True
    ClientClass = GdsCloudtrailClient
    is_regional = False
    resource_type = 'AWS::CLOUDTRAIL:LOG_VALIDATION'
    title = 'Cloud Trail: Multi-regional'
    description = (
        'Logs validation is not enabled for trail.'
    )
    why_is_it_important = (
         'BLABLA'
    )
    how_do_i_fix_it = (
         'BLABLA'
    )


    def get_data(self, session, **kwargs):
        try:
            return self.client.describe_trails(session)
        except Exception as e:
            self.app.log.error(self.app.utilities.get_typed_exception(e))
            return []


    def translate(self, data={}):
        return {
            'region': data['HomeRegion'],
            'resource_id': data['TrailARN'],
            'resource_name': data['Name'],
        }


    def evaluate(self, event, item, whitelist=[]):
        if item['LogFileValidationEnabled'] == True:
            compliance_type = 'COMPLIANT'
            self.annotation = ''
        else:
            compliance_type = 'NON_COMPLIANT'
            self.annotation = f'The Trail "{item["Name"]}" in region "{item["HomeRegion"]}" has logging validation disabled.'
        return self.build_evaluation(
              item['TrailARN'],
              compliance_type,
              event,
              self.resource_type,
              self.annotation
    )
