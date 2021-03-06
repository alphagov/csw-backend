"""
implements aws::s3::bucket_permissions
checkId: Pfx0RwqBli
Checks on the S3 bucket permissions that can potentially compromise files.
"""
from chalicelib.criteria.criteria_default import TrustedAdvisorCriterion
from chalicelib.aws.gds_s3_client import GdsS3Client


class S3BucketPermissions(TrustedAdvisorCriterion):
    """
    Subclass Criterion checking against S3 bucket permissions.
    """

    ResourceClientClass = GdsS3Client

    active = False

    def __init__(self, app):
        self.resource_type = "AWS::s3::bucket_permissions"
        self.check_id = "Pfx0RwqBli"
        super(S3BucketPermissions, self).__init__(app)

    def translate(self, data={}):
        return {
            "region": data.get("region", ""),
            "resource_id": data.get("resourceId", ""),
            # bucket name
            "resource_name": data.get("metadata", [0, 1, None])[2],
        }

    def get_resource_data(self, session, region, resource):
        name = resource.get("metadata", [0, 1, None])[2]
        bucket_acl = None
        if name:
            bucket_acl = self.resource_client.get_bucket_acl(session, name)
        return bucket_acl


class S3BucketReadAll(S3BucketPermissions):
    """
    Subclass Criterion checking for list permission to all.
    """

    active = True
    severity = 2

    def __init__(self, app):
        self.title = 'S3 Bucket ACLs: Does not allow List access for "Everyone" or "Any Authenticated AWS User"'
        self.description = (
            "Checks that there are no S3 buckets with ACLs allowing open List access or allowing List access to any "
            "authenticated AWS user in your account."
        )
        self.why_is_it_important = (
            "If a bucket has world upload/delete permissions, this allows anyone to create, "
            "modify and delete files in the S3 bucket; this can clearly cause issues. <br />"
            "However, even “List” permissions being open to the world can cause problems "
            "- malicious individuals can rack up costs on a bucket by repeatedly listing documents on a bucket. <br />"
            "Therefore it’s vital to secure all S3 buckets by making sure "
            "that they are closed to everyone outside of GDS."
        )
        self.how_do_i_fix_it = (
            "Change the bucket permissions ACL Everyone options to remove list permissions."
        )
        super(S3BucketReadAll, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = "NON_COMPLIANT"
        if item["metadata"][3] == "Yes":
            self.annotation = (
                f'Bucket "{item["metadata"][2]}" in region "{item["metadata"][0]}" policy allows "everyone" '
                f'or "any authenticated AWS user" to list its contents.'
            )
        else:
            compliance_type = "COMPLIANT"
            # Remove any previous annotation if instance is reused
            self.annotation = ""
        return self.build_evaluation(
            item["resourceId"],
            compliance_type,
            event,
            self.resource_type,
            self.annotation,
        )


class S3BucketOpenAccess(S3BucketPermissions):
    """
    Subclass Criterion checking for open access permission.
    """

    active = True

    def __init__(self, app):
        self.title = "S3 Bucket Policies: Does not allow open access"
        self.description = "Checks that there are no S3 buckets with a bucket policy allowing open access."
        self.why_is_it_important = (
            "If a bucket has world upload/delete permissions, this allows anyone to create, "
            "modify and delete files in the S3 bucket; this can clearly cause issues. <br />"
            "However, even “List” permissions being open to the world can cause problems "
            "- malicious individuals can rack up costs on a bucket by repeatedly listing documents on a bucket. <br />"
            "Therefore it’s vital to secure all S3 buckets by making sure "
            "that they are closed to everyone outside of GDS."
        )
        self.how_do_i_fix_it = (
            "Change the bucket permissions ACL Everyone options to remove the <strong>List objects</strong> permission."
        )
        super(S3BucketOpenAccess, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = "NON_COMPLIANT"
        if item["metadata"][6] == "Yes":
            self.annotation = (
                "The bucket ACL Everyone <strong>List objects</strong> permission is enabled."
            )
        else:
            compliance_type = "COMPLIANT"
        return self.build_evaluation(
            item["resourceId"],
            compliance_type,
            event,
            self.resource_type,
            self.annotation,
        )


class S3BucketWriteAll(S3BucketPermissions):
    """
    Subclass Criterion checking for update/delete permission to all.
    """

    active = True

    def __init__(self, app):
        self.title = 'S3 Bucket ACLs: Does not allow Upload or Delete access for "Everyone" or "Any Authenticated AWS User"'
        self.description = (
            "Checks that there are no S3 buckets with ACLs allowing with open Upload / Delete access or allowing Upload"
            " / Delete access to any authenticated AWS user in your account."
        )
        self.why_is_it_important = (
            "If a bucket has world upload/delete permissions, this allows anyone to create, "
            "modify and delete files in the S3 bucket; this can clearly cause issues. <br />"
            "However, even “List” permissions being open to the world can cause problems "
            "- malicious individuals can rack up costs on a bucket by repeatedly listing documents on a bucket. <br />"
            "Therefore it’s vital to secure all S3 buckets by making sure "
            "that they are closed to everyone outside of GDS."
        )
        self.how_do_i_fix_it = (
            "Change the bucket permissions ACL Everyone options to remove the <strong>Write objects</strong> permission."
        )
        super(S3BucketWriteAll, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = "NON_COMPLIANT"
        if item["metadata"][4] == "Yes":
            self.annotation = (
                "The bucket ACL Everyone <strong>Write objects</strong> permission is enabled."
            )
        else:
            compliance_type = "COMPLIANT"
        return self.build_evaluation(
            item["resourceId"],
            compliance_type,
            event,
            self.resource_type,
            self.annotation,
        )
