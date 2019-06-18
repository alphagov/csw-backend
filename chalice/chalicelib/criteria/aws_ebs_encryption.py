"""
"""
from chalicelib.aws.gds_ec2_client import GdsEc2Client
from chalicelib.criteria.criteria_default import CriteriaDefault


class EbsEncryption(CriteriaDefault):
    """
    """

    active = True
    ClientClass = GdsEc2Client
    is_regional = True
    resource_type = "AWS::EBS::ENCRYPTION"
    title = "EBS: Encryption Enabled"
    description = "An unencrypted volume has been found in this region."
    why_is_it_important = (
        "Enabling encryption in your EBS volumes will protect your data at rest from unauthorized access or theft. "
        "Encrypting your data can help to satisfy information security or "
        "regulatory requirements such as the Payment Card Industry Data Security Standard (PCI DSS)."
    )
    how_do_i_fix_it = (
        "To enable encryption for a new EBS Volume, follow the below steps:"
        "<ol>"
        "<li>From within the AWS Management Console, select EC2</li>"
        '<li>Under "Elastic Block Store" select "Volumes"</li>'
        '<li>Select "Create Volume"</li>'
        "<li>Enter the required configuration for your Volume</li>"
        '<li>Select the checkbox for "Encrypt this volume"</li>'
        '<li>Select the KMS Customer Master Key (CMK) to be used under "Master Key"</li>'
        '<li>Select "Create Volume"</li>'
        "</ol>"
        "Once your volume has been created, "
        "all data saved to this volume will be encrypted when attached to an EC2 instance.<br />"
        "To encrypt an existing unencrypted EBS Volume, follow the below steps:"
        "<ol>"
        "<li>Select your unencrypted volume</li>"
        '<li>Select "Actions" – "Create Snapshot"</li>'
        '<li>When the snapshot is complete, select "Snapshots" under "Elastic Block Store" '
        "Select your newly created snapshot</li>"
        '<li>Select "Actions" – "Copy"</li>'
        '<li>Check the box for "Encryption"</li>'
        "<li>Select the CMK for KMS to use as required</li>"
        '<li>Click "Copy"</li>'
        "<li>Select the newly created snapshot</li>"
        '<li>Select "Actions" – "Create Volume"</li>'
        '<li>You will notice that the normal "Encryption" option is set to "True".</li>'
        "</ol>"
        "For further information, please see the "
        '<a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSEncryption.html">AWS documentation</a>.'
    )

    def get_data(self, session, **kwargs):
        home_volumes = []
        try:
            for vol in self.client.describe_volumes(session):
                if vol["AvailabilityZone"].startswith(kwargs["region"]):
                    home_volumes.append(vol)
        except Exception:
            self.app.log.error(self.app.utilities.get_typed_exception())
        return home_volumes

    def translate(self, data={}):
        return {
            "region": data["AvailabilityZone"],
            "resource_id": data["VolumeId"],
            "resource_name": data["VolumeId"],
        }

    def evaluate(self, event, item, whitelist=[]):
        if item["Encrypted"]:
            compliance_type = "COMPLIANT"
            self.annotation = ""
        else:
            compliance_type = "NON_COMPLIANT"
            self.annotation = "This EBS volume is not encrypted."
        return self.build_evaluation(
            item["VolumeId"],
            compliance_type,
            event,
            self.resource_type,
            self.annotation,
        )
