"""
implements AWS::RDS::PublicSnapshots
checkId: ePs02jT06w
"""
from chalicelib.criteria.criteria_default import TrustedAdvisorCriterion


class RDSPublicSnapshot(TrustedAdvisorCriterion):
    """
    """
    active = True

    def __init__(self, app):
        self.resource_type = 'AWS::RDS::PublicSnapshots'
        self.check_id = 'xSqX82fQu'
        self.title = 'RDS Snapshots: There are no public snapshots'
        self.description = (
            'Checks the permission settings for your Amazon Relational Database Service (Amazon RDS) DB snapshots '
            'and alerts you if any snapshots are marked as public. '
        )
        self.why_is_it_important = (
            'When you make a snapshot public, you give all AWS accounts '
            'and users access to all the data on the snapshot. <br />'
            'If you want to share a snapshot with particular users or accounts, mark the snapshot as private, '
            'and then specify the user or accounts you want to share the snapshot data with. <br />'
            'Note: Results for this check are automatically refreshed several times daily, '
            'and refresh requests are not allowed. <br />'
            'It might take a few hours for changes to appear.'
        )
        self.how_do_i_fix_it = (
            'Unless you are certain you want to share all the data in the snapshot with all AWS accounts and users, '
            'modify the permissions: mark the snapshot as private, '
            'and then specify the accounts that you want to give permissions to. <br />'
            'For more information, see Sharing a DB Snapshot or DB Cluster Snapshot for this '
            '<a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ShareSnapshot.html">link</a>.'
        )
        super(RDSPublicSnapshot, self).__init__(app)

    def translate(self, data={}):
        return {
            'region': data.get('region', ''),
            'resource_id': data.get('resourceId', ''),
            'resource_name': data.get('metadata', ['', '', '', '', ])[3],  # snapshot ID or empty string
        }

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = 'COMPLIANT'
        if item['status'] == 'error':
            compliance_type = 'NON_COMPLIANT'
            self.annotation = (
                f'The snapshot with ID "{item["metadata"][3]}" '
                f'of the DB instance or cluster with ID "{item["metadata"][2]}" '
                f'in the region "{item["metadata"][1]}" is marked as "public".'
            )
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )
