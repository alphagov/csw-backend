"""
implements aws::s3::bucket_permissions
checkId: Pfx0RwqBli
Checks on the S3 bucket permissions that can potentially compromise files.
"""
import json

from chalicelib.criteria.criteria_default import CriteriaDefault
from chalicelib.aws.gds_support_client import GdsSupportClient


class S3BucketPermissions(CriteriaDefault):
    """
    Subclass Criterion checking against S3 bucket permissions.
    """
    active = False

    def __init__(self, app):
        # attributes to overwrite in subclasses
        self.status_string = ''
        self.status_interval = ''
        # attributes common in both subclasses
        self.resource_type = 'AWS::s3::bucket_permissions'
        self.ClientClass = GdsSupportClient
        self.check_id = 'Pfx0RwqBli'
        self.language = 'en'
        self.region = 'us-east-1'
        self.annotation = ''
        super(S3BucketPermissions, self).__init__(app)

    def get_data(self, session, **kwargs):
        output = self.client.describe_trusted_advisor_check_result(
            session,
            checkId=self.check_id,
            language=self.language
        )
        self.app.log.debug(json.dumps(output))
        return output['flaggedResources']  # will have len() == 0 if compliant or non-applicable

    def translate(self, data={}):
        return {
            'resource_id': 'root',
            'resource_name': 'Root Account',
        }


class S3BucketReadAll(S3BucketPermissions):
    """
    Subclass Criterion checking for list permission to all.
    """
    active = True

    def __init__(self, app):
        self.title = (
            'S3 Bucket Permissions: The bucket ACL allows List access '
            'for "Everyone" or "Any Authenticated AWS User"'
        )
        self.description = (
            'There are S3 buckets with open access permissions '
            'or allow access to any authenticated AWS user in your account.'
        )
        self.why_is_it_important = (
            'If a bucket has world upload/delete permissions, this allows anyone to create, '
            'modify and delete files in the S3 bucket; this can clearly cause issues. '
            'However, even “List” permissions being open to the world can cause problems '
            '- malicious individuals can rack up costs on a bucket by repeatedly listing documents on a bucket. '
            'Therefore it’s vital to secure all S3 buckets by making sure '
            'that they are closed to everyone outside of GDS.'
        )
        self.how_do_i_fix_it = (
            'Review the permissions on the listed buckets, and change them to make sure '
            'that they are no longer open.'
        )
        super(S3BucketReadAll, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        compliance_type = 'NON_COMPLIANT'
        if item["metadata"][3] == 'Yes':
            self.annotation = (
                f'Bucket "{item["metadata"][2]}" in region "{item["metadata"][0]}" policy allows "everyone" '
                f'or "any authenticated AWS user" to list its contents'
            )
        else:
            compliance_type = 'COMPLIANT'
        return self.build_evaluation(
            item['resourceId'],
            compliance_type,
            event,
            self.resource_type,
            self.annotation
        )


class S3BucketOpenAccess(S3BucketPermissions):
    """
    Subclass Criterion checking for open access permission.
    """
    active = True

    def __init__(self, app):
        self.title = (
            'S3 Bucket Permissions:  A bucket policy allows any kind of open access.'
        )
        self.description = (
            'There are S3 buckets with open access permissions or '
            'allow access to any authenticated AWS user in your account.'
        )
        self.why_is_it_important = (
            'If a bucket has world upload/delete permissions, this allows anyone to create, '
            'modify and delete files in the S3 bucket; this can clearly cause issues. '
            'However, even “List” permissions being open to the world can cause problems '
            '- malicious individuals can rack up costs on a bucket by repeatedly listing documents on a bucket. '
            'Therefore it’s vital to secure all S3 buckets by making sure '
            'that they are closed to everyone outside of GDS.'
        )
        self.how_do_i_fix_it = (
            'Review the permissions on the listed buckets, and change them to make sure that they are no longer open.'
        )
        super(S3BucketOpenAccess, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        pass


class S3BucketWriteAll(S3BucketPermissions):
    """
    Subclass Criterion checking for update/delete permission to all.
    """
    active = True

    def __init__(self, app):
        self.title = (
            'S3 Bucket Permissions:  The bucket ACL allows Upload/Delete access '
            'for "Everyone" or "Any Authenticated AWS User".'
        )
        self.description = (
            'There are S3 buckets with open access permissions or allow access '
            'to any authenticated AWS user in your account.'
        )
        self.why_is_it_important = (
            'If a bucket has world upload/delete permissions, this allows anyone to create, '
            'modify and delete files in the S3 bucket; this can clearly cause issues. '
            'However, even “List” permissions being open to the world can cause problems '
            '- malicious individuals can rack up costs on a bucket by repeatedly listing documents on a bucket. '
            'Therefore it’s vital to secure all S3 buckets by making sure '
            'that they are closed to everyone outside of GDS.'
        )
        self.how_do_i_fix_it = (
            'Review the permissions on the listed buckets, and change them to make sure that they are no longer open.'
        )
        super(S3BucketWriteAll, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        pass
