from chalicelib.aws.gds_cloudtrail_client import GdsCloudtrailClient
from chalicelib.criteria.criteria_default import CriteriaDefault


class CloudTrailFileValidation(CriteriaDefault):
    """
    """
    active = True
    ClientClass = GdsCloudtrailClient
    is_regional = False
    resource_type = 'AWS::CLOUDTRAIL:LOG_VALIDATION'
    title = 'Cloud Trail: Log File Validation'
    description = (
        'Log file validation makes it computationally infeasible to modify, delete or forge CloudTrail log files without detection.'
    )
    why_is_it_important = (
         'Validated log files are invaluable in security and forensic investigations.'
         'For example, a validated log file enables you to assert positively that the log file itself has not changed,'
         'or that particular user credentials performed specific API activity. The CloudTrail log file integrity '
         'validation process also lets you know if a log file has been deleted or changed, or assert positively'
         'that no log files were delivered to your account during a given period of time.'
    )
    how_do_i_fix_it = (
         'To enable log file integrity validation, you can use the AWS Management Console, the AWS CLI,'
         'or CloudTrail API. For more information, '
         'see <a href="https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-enabling.html">Enabling '
         'Log File Integrity Validation for CloudTrail</a>.<br />'
         'To validate the integrity of CloudTrail log files, you can use the AWS CLI or create your own solution.'
         'The AWS CLI will validate files in the location where CloudTrail delivered them. If you want to validate'
         'logs that you have moved to a different location, either in Amazon S3 or elsewhere, you can create your own validation tools.<br />'
         'For information on validating logs by using the AWS CLI, see <a href="https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-cli.html">Validating CloudTrail Log File Integrity with the AWS CLI</a>. For information on developing custom implementations of CloudTrail log file validation, see <a href="https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-custom-validation.html">Custom Implementations of CloudTrail Log File Integrity Validation</a>.'
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
            self.annotation = f'The Trail "{item["Name"]}" in region "{item["HomeRegion"]}" has log file validation disabled.'
        return self.build_evaluation(
              item['TrailARN'],
              compliance_type,
              event,
              self.resource_type,
              self.annotation
    )
