"""
"""
from chalicelib.aws.gds_rds_client import GdsRdsClient
from chalicelib.criteria.criteria_default import CriteriaDefault


class RdsEncryption(CriteriaDefault):
    """
    """

    active = True
    severity = 3

    ClientClass = GdsRdsClient
    is_regional = True
    resource_type = "AWS::RDS::ENCRYPTION"
    title = "RDS: Encryption Enabled"
    description = "The data stored on the following RDS resources is not encrypted."
    why_is_it_important = (
        "Enabling encryption in RDS resources protects sensitive data stored in your database "
        "from unauthorized access or theft."
    )
    how_do_i_fix_it = (
        "To enable encryption to new RDS database instance, follow these "
        '<a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Encryption.html#Overview.Encryption.Enabling">instructions</a>.<br />'
        "To enable RDS encryption to an existing unencrypted database, "
        "create a snapshot of your DB instance, "
        "and then create an encrypted copy of that snapshot. <br />"
        "You can then restore a DB instance from the encrypted snapshot, "
        "and thus you have an encrypted copy of your original DB instance.<br />"
        "<b>Note:</b> Once you have tested the new encrypted RDS copy, "
        "consider removing the original unencrypted database "
        "and all previous snapshots created when encryption was disabled.<br />"
        "Further information can be found at following AWS links: "
        '<a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Encryption.html">Encrypting RDS resources</a>, '
        '<a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_CopySnapshot.html">Copy a Snapshot</a>'
    )

    def get_data(self, session, **kwargs):
        home_db_instances = []
        try:
            for db in self.client.describe_db_instances(session):
                if db["AvailabilityZone"].startswith(kwargs["region"]):
                    home_db_instances.append(db)
        except Exception:
            self.app.log.error(self.app.utilities.get_typed_exception())
        return home_db_instances

    def translate(self, data={}):
        return {
            "region": data["AvailabilityZone"],
            "resource_id": data["DbiResourceId"],
            "resource_name": data["DBInstanceIdentifier"],
        }

    def evaluate(self, event, item, whitelist=[]):
        # is storage encryption enabled
        if item["StorageEncrypted"] is True:
            compliance_type = "COMPLIANT"
            self.annotation = ""
        # don't fail stopped or deleting instances
        elif item["DBInstanceStatus"] in ["stopped", "deleting"]:
            compliance_type = "COMPLIANT"
            self.annotation = ""
        else:
            compliance_type = "NON_COMPLIANT"
            self.annotation = "This database instance is not encrypted."
        return self.build_evaluation(
            item["DbiResourceId"],
            compliance_type,
            event,
            self.resource_type,
            self.annotation,
        )
