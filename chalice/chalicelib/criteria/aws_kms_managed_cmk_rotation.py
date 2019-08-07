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
    title = "Key Management Service: Custom Master Keys rotated annually by the service"
    description = (
        "Cryptographic best practices discourage extensive reuse of encryption keys. "
        "To create new cryptographic material for your Key Management Service (KMS) customer master keys (CMKs), "
        "you can create new CMKs, and then change your applications "
        "or aliases to use the new CMKs or you can enable automatic key rotation for an existing CMK. "
        "Automatic key rotation for a customer managed CMK generates new cryptographic material for it every year. "
        "KMS also saves the CMK's older cryptographic material to be used to decrypt data that it encrypted.<br />"
        "Key rotation changes only the CMK's backing key, "
        "which is the cryptographic material that is used in encryption operations. "
        "The CMK is the same logical resource, regardless of whether or how many times its backing key changes. "
        "The properties of the CMK do not change, as shown in the following image."
    )
    why_is_it_important = (
        "<ul>"
        "<li>The properties of the CMK, including its key ID, key ARN, region, policies, and permissions, "
        "do not change when the key is rotated.</li>"
        "<li>You do not need to change applications or aliases that refer to the CMK ID or ARN.</li>"
        "<li>After you enable key rotation, AWS KMS rotates the CMK automatically every year. "
        "You do not need to remember or schedule the update.</li>"
        "</ul>"
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
