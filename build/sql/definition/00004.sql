UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_cloudtrail_logging.CloudtrailLogHasErrors' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_cloudtrail_logging.CloudtrailLogHasErrors'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_cloudtrail_logging.CloudtrailLogNotInRegion' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_cloudtrail_logging.CloudtrailLogNotInRegion'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_cloudtrail_logging.CloudtrailLogTurnedOff' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_cloudtrail_logging.CloudtrailLogTurnedOff'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_cloudtrail_logging.CloudtrailLogNotToCST' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_cloudtrail_logging.CloudtrailLogNotToCST'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_ebs_public_snapshots.EBSPublicSnapshot' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_ebs_public_snapshots.EBSPublicSnapshot'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_elb_listener_security.ELBListenerSecurityNoListener' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_elb_listener_security.ELBListenerSecurityNoListener'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_elb_listener_security.ELBListenerSecurityPredefinedOutdated' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_elb_listener_security.ELBListenerSecurityPredefinedOutdated'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_elb_listener_security.ELBListenerSecurityProtocolDiscouraged' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_elb_listener_security.ELBListenerSecurityProtocolDiscouraged'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_elb_listener_security.ELBListenerSecurityInsecureProtocol' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_elb_listener_security.ELBListenerSecurityInsecureProtocol'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_elb_security_groups.ELBSecurityGroupsRed' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_elb_security_groups.ELBSecurityGroupsRed'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_elb_security_groups.ELBSecurityGroupsYellow' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_elb_security_groups.ELBSecurityGroupsYellow'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_access_key_exposed.AwsIamPotentiallyExposedAccessKey' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_exposed_key.AwsIamPotentiallyExposedAccessKey'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_access_key_exposed.AwsIamSuspectedExposedAccessKey' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_exposed_key.AwsIamSuspectedExposedAccessKey'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_access_key_rotation.AwsIamAccessKeyRotationYellow' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_iam_access_key_rotation.AwsIamAccessKeyRotationYellow'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_access_key_rotation.AwsIamAccessKeyRotationRed' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_iam_access_key_rotation.AwsIamAccessKeyRotationRed'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_rds_public_snapshots.RDSPublicSnapshot' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_rds_public_snapshots.RDSPublicSnapshot'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_s3_bucket_permissions.S3BucketReadAll' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_s3_bucket_permissions.S3BucketReadAll'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_s3_bucket_permissions.S3BucketOpenAccess' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_s3_bucket_permissions.S3BucketOpenAccess'
);

UPDATE criterion 
SET invoke_class_name='chalicelib.criteria.aws_support_s3_bucket_permissions.S3BucketWriteAll' 
WHERE invoke_class_name=(
    SELECT invoke_class_name 
    FROM criterion 
    WHERE invoke_class_name='chalicelib.criteria.aws_s3_bucket_permissions.S3BucketWriteAll'
);
