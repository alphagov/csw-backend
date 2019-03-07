"""
"""
from chalicelib.aws.gds_rds_client import GdsRdsClient
from chalicelib.criteria.criteria_default import CriteriaDefault


class RdsEncryption(CriteriaDefault):
    """
    """
    active = True
    ClientClass = GdsRdsClient
    is_regional = False
    resource_type = 'AWS::RDS::ENCRYPTION'
    title = 'Relational Database Service: Encryption Enabled'
    description = (
        'The data stored on the following RDS resources is not encrypted.'
    )
    why_is_it_important = (
        'Enabling encryption in RDS resources protects sensitive data stored in your database '
        'from unauthorized access or theft.'
    )
    how_do_i_fix_it = (
        'To enable encryption to new RDS database instance, follow these '
        '<a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Encryption.html#Overview.Encryption.Enabling">instructions</a>.<br />'
        'To enable RDS encryption to an existing unencrypted database, '
        'create a snapshot of your DB instance, '
        'and then create an encrypted copy of that snapshot. <br />'
        'You can then restore a DB instance from the encrypted snapshot, '
        'and thus you have an encrypted copy of your original DB instance.<br />'
        '<b>Note:</b> Once you have tested the new encrypted RDS copy, '
        'consider removing the original unencrypted database '
        'and all previous snapshots created when encryption was disabled.<br />'
        'Further information can be found at following AWS links: '
        '<a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Encryption.html">Encrypting RDS resources</a>, '
        '<a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_CopySnapshot.html">Copy a Snapshot</a>'
    )

    
    def get_data(self, session, **kwargs):
        pass

    def translate(self, data={}):
        pass

    def evaluate(self, event, item, whitelist=[]):
        pass
