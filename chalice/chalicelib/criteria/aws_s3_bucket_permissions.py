"""
implements aws::s3::bucket_permissions
checkId: Pfx0RwqBli
Checks on the S3 bucket permissions that can potentially compromise files.
"""

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
        pass

    def translate(self, data={}):
        pass


class S3BucketReadAll(S3BucketPermissions):
    """
    Subclass Criterion checking for list permission to all.
    """
    active = True

    def __init__(self, app):
        super(S3BucketReadAll, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        pass


class S3BucketOpenAccess(S3BucketPermissions):
    """
    Subclass Criterion checking for open access permission.
    """
    active = True

    def __init__(self, app):
        super(S3BucketOpenAccess, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        pass


class S3BucketWriteAll(S3BucketPermissions):
    """
    Subclass Criterion checking for update/delete permission to all.
    """
    active = True

    def __init__(self, app):
        super(S3BucketWriteAll, self).__init__(app)

    def evaluate(self, event, item, whitelist=[]):
        pass
