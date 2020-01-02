"""
"""
from chalicelib.aws.gds_kms_client import GdsKmsClient
from chalicelib.criteria.criteria_default import CriteriaDefault


class ManagedCmkRotation(CriteriaDefault):
    """
    """

    active = True
    severity = 2
    ClientClass = GdsKmsClient
    is_regional = False
    resource_type = "AWS::KMS:CMK_ROTATION"
    title = (
        "Key Management Service: Customer Master Keys rotated annually by the service"
    )
    description = (
        "Checks whether a Customer Managed Key (CMK) has automatic key rotation enabled. If not, "
        "this can either be because automatic rotation was not turned on, or the CMK is of a "
        "type that does not support automatic key rotation, such as a CMK with imported key "
        "material."
    )
    why_is_it_important = (
        "Cryptographic best practices discourage extensive reuse of encryption keys. This is "
        "to reduce the impact of to the organisation when a key leaks - if data is encrypted "
        "regularly with the same key for a period of years, if that key gets leaked, all that data "
        "is now compromised. If the keys were regularly changed, the amount of compromised data is "
        "limited."
    )
    how_do_i_fix_it = (
        "To activate automatic annual rotation for your CMKs follow the steps below:<br />"
        "<ol>"
        "<li>Sign in to the AWS Management Console.</li>"
        "<li>Open the AWS Key Management Service (AWS KMS) console.</li>"
        "<li>Change your region to the CMS' region found under reason.</li>"
        "<li>In the navigation pane, choose Customer managed keys.</li>"
        "<li>Choose the alias or key ID of a CMK.</li>"
        "<li>Under General configuration, choose the Key rotation tab.</li>"
        "<li>Select or clear the Automatically rotate this CMK every year check box.</li>"
        "<li>Choose Save.</li>"
        "</ol>"
        "If the CMK was created without key material (its Origin is EXTERNAL), there is no Key rotation tab. "
        "You cannot automatically rotate these CMK.<br />"
        "If a CMK is disabled or pending deletion, "
        "the Automatically rotate this CMK every year check box is cleared, "
        "and you cannot change it. "
        "The key rotation status is restored when you enable the CMK or cancel deletion.<br />"
        "For more information and options read the AWS "
        '<a href="https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html">documentation</a>.'
    )

    def __init__(self, app):
        super(ManagedCmkRotation, self).__init__(app)

    def get_data(self, session, **kwargs):
        try:
            return self.client.get_key_list_with_details(session)
        except Exception:
            self.app.log.error(self.app.utilities.get_typed_exception())
            return []

    def translate(self, data={}):
        return {
            "region": data["KeyArn"].split(":")[3],
            "resource_id": data["KeyId"],
            "resource_name": data["KeyId"],
        }

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = "NON_COMPLIANT"
        self.annotation = f'The CMK "{item["KeyArn"]}" is non-rotating, enabled and not scheduled for deletion.'
        if item["KeyRotationEnabled"] or not item["Enabled"] or "DeletionDate" in item:
            compliance_type = "COMPLIANT"
            self.annotation = ""
        return self.build_evaluation(
            item["KeyId"], compliance_type, event, self.resource_type, self.annotation
        )
