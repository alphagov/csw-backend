/**
  Create database, user, define schema and populate with default data.

  This doesn't create any product teams or account subscriptions
*/
const gulp = require('gulp');
const args = require('yargs').argv;
const data = require('gulp-data');
const modifyFile = require('gulp-modify-file');
const exec = require('child-process-promise').exec;
const awsParamStore = require('aws-param-store');
const fs = require('fs');

console.log(process.cwd());
const helpers = require(process.cwd()+"/gulp_helpers/helpers.js");

gulp.task('environment.database_create', function() {

  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  var config = helpers.getConfigLocations(env, tool);

  // Load settings file
  var pipeline = gulp.src(config.files.environment_settings)
  // Parse settings into file.data
  .pipe(modifyFile(function(content, path, file) {
    var settings = JSON.parse(content);
    file.data = settings;
    return content;
  }))
  // Get RDS root password from parameter store
  // Add to file.data
  .pipe(data(function(file) {

    var parameter = '/csw/'+env+'/rds/root';
    var property = 'postgres_root_password';
    return helpers.getParameterInPipelinePromise(parameter, file.data.region, file, property);

  }))
  // Get RDS user password from parameter store
  // Add to file.data
  .pipe(data(function(file) {

    var parameter = '/csw/'+env+'/rds/user';
    var property = 'postgres_user_password';
    return helpers.getParameterInPipelinePromise(parameter, file.data.region, file, property);

  }))
  // Pass commands to psql_tunnel.py script
  .pipe(data(function(file) {

    path = config.paths.root + "/build/gulp_helpers";

    command = "CREATE DATABASE " + file.data.tool + ";";

    var promise = helpers.psqlExecuteInPipelinePromise(path, command, file)
    .then(function(output) {
        var command = "CREATE USER cloud_sec_watch WITH ENCRYPTED PASSWORD '"+file.data.postgres_user_password+"';";
        return helpers.psqlExecuteInPipelinePromise(path, command, file)
    })
    .then(function(output) {
        var command = "GRANT ALL PRIVILEGES ON DATABASE csw TO cloud_sec_watch;";
        return helpers.psqlExecuteInPipelinePromise(path, command, file)
    });

    return promise;

  }));

  return pipeline;

});

gulp.task('environment.database_create_tables', function() {

  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  var config = helpers.getConfigLocations(env, tool);

  // Load default chalice config file

  var pipeline = gulp.src(config.files.environment_settings)
  // Read settings into file.data
  .pipe(modifyFile(function(content, path, file) {
    var settings = JSON.parse(content);
    file.data = settings;
    return content;
  }))
  .pipe(data(function(file) {

    var payload = {
        "Tables":[
            "User",
            "UserSession",
            "ProductTeam",
            "AccountSubscription",
            "AccountAudit",
            "AccountLatestAudit",
            "Status",
            "Severity",
            "CriteriaProvider",
            "Criterion",
            "CriterionParams",
            "AuditCriterion",
            "AuditResource",
            "ResourceCompliance",
            "ResourceRiskAssessment"
        ]
    };

    var function_name = "csw-"+env+"-database_create_tables";
    var output_file = config.paths.environment + "/lambda.out"
    var working = config.paths.environment;

    return helpers.lambdaInvokePromise(function_name, working, payload, file, output_file);

  }))
  .pipe(data(function(file) {

    var file = config.paths.environment + "/lambda.out"
    output = JSON.parse(fs.readFileSync(file));
    console.log(output);

  }));

  return pipeline;


});


gulp.task('environment.database_populate', function() {

  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  var config = helpers.getConfigLocations(env, tool);

  // Load default chalice config file
  var payloads = {
    "Items": [
        {
            "Model":"Status",
            "Params":{
                "status_name": "Unknown",
                "description": "Not yet evaluated"
            }
        },
        {
            "Model":"Status",
            "Params":{
                "status_name": "Pass",
                "description": "Compliant or not-applicable"
            }
        },
        {
            "Model":"Status",
            "Params":{
                "status_name": "Fail",
                "description": "Non-compliant"
            }
        },
        {
            "Model":"CriteriaProvider",
            "Params":{
                "provider_name":"AWS Trusted Advisor"
            }
        },
        {
            "Model":"CriteriaProvider",
            "Params":{
                "provider_name":"AWS Elastic Cloud Compute (EC2) service"
            }
        },
        {
            "Model":"CriteriaProvider",
            "Params":{
                "provider_name":"AWS Identity and Access Management (IAM) service"
            }
        },
        {
            "Model":"Criterion",
            "Params":{
                "criterion_name":"Security Groups - SSH ingress enabled from unknown IPs",
                "criteria_provider_id":2,
                "invoke_class_name":"chalicelib.criteria.aws_ec2_security_group_ingress_ssh.AwsEc2SecurityGroupIngressSsh",
                "invoke_class_get_data_method": "describe_security_groups",
                "title": "Security Groups - SSH ingress enabled from unknown IPs",
                "description": "If SSH is enabled into a VPC it should be limited to known IPs",
                "why_is_it_important": "If someone has access to either one of our WiFis or our VPN then there is more chance they should have access",
                "how_do_i_fix_it": "In almost all cases, SSH ingress should be limited to the <a target=\"gds-wiki\" href=\"https://sites.google.com/a/digital.cabinet-office.gov.uk/gds-internal-it/news/whitechapel-sourceipaddresses\">GDS public IPs</a>. There may be exceptions where we are working closely in partnership with another organisation."
            }
        },
        {
            "Model":"Criterion",
            "Params":{
                "criterion_name":"Security Groups - Ingress open for flagged ports",
                "criteria_provider_id":2,
                "invoke_class_name":"chalicelib.criteria.aws_ec2_security_group_ingress_open.AwsEc2SecurityGroupIngressOpen",
                "invoke_class_get_data_method": "describe_security_groups",
                "title": "Security Groups - Ingress open for flagged ports",
                "description": "Unrestricted inbound connections should not be allowed for certain ports",
                "why_is_it_important": "By opening ports like FTP or common database connection ports to the world you dramatically increase the risk to your service",
                "how_do_i_fix_it": "Change unrestricted CIDR to an internal IP range or a whitelist of specific IP addresses"
            }
        },
        {
            "Model":"Criterion",
            "Params":{
                "criterion_name":"MFA on Root Account",
                "criteria_provider_id":1,
                "invoke_class_name":"chalicelib.criteria.aws_support_root_mfa.AwsSupportRootMfa",
                "invoke_class_get_data_method": "get_root_mfa_status_data",
                "title": "Multi-Factor Authentication enabled for root user on account",
                "description": "Checks the root account and warns if multi-factor authentication (MFA) is not enabled. For increased security, we recommend that you protect your account by using MFA, which requires a user to enter a unique authentication code from their MFA hardware or virtual device when interacting with the AWS console and associated websites.",
                "why_is_it_important": "MFA on root is not enabled. If the account gets compromised, an attacker will be able to access all resources in the root account, deleting configuration, creating resources for malicious activity or to lunch further attacks.",
                "how_do_i_fix_it": "If you have the root credentials for your account enable MFA - otherwise speak to Tech-ops Reliability Engineering <a target=\"slack\" href=\"https://gds.slack.com/messages/reliability-eng/\">#reliability-engineering</a>",
                "active": false,
                "is_regional": false
            }
        },
        {
            "Model":"Criterion",
            "Params":{
                "criterion_name":"IAM inspector policy is up-to-date",
                "criteria_provider_id":3,
                "invoke_class_name":"chalicelib.criteria.aws_iam_validate_inspector_policy.AwsIamValidateInspectorPolicy",
                "invoke_class_get_data_method":"get_inspector_role_policy_data",
                "title":"Inspector policy is up-to-date",
                "description":"Checks whether the Cloud Security Watch role matches the current definition on GitHub.",
                "why_is_it_important":"If the role policy does not grant the correct permissions checks will fail to be processed.",
                "how_do_i_fix_it":"Update the module and re-run the terraform apply to re-deploy the role and policy statements.",
                "active": false,
                "is_regional": false
            }
        },
        {
            "Model":"Criterion",
            "Params":{
                "criterion_name":"IAM Access Key Rotation > 90 days",
                "criteria_provider_id":2,
                "invoke_class_name":"chalicelib.criteria.aws_iam_access_key_rotation.AwsIamAccessKeyRotationYellow",
                "invoke_class_get_data_method": "describe_trusted_advisor_check_result",
                "title": "IAM Access Key Rotation Yellow",
                "description": "At least one active Identity and Access Management (IAM) access key has not been rotated in the last 90 days",
                "why_is_it_important": "Rotating IAM credentials periodically will significantly reduce the chances that a compromised set of access keys can be used without your knowledge to access certain components within your AWS account.",
                "how_do_i_fix_it": "Ensure that all your IAM user access keys are rotated at least every 90 days in order to decrease the likelihood of accidental exposures and protect your AWS resources against unauthorized access. To rotate access keys, it is recommended to follow these steps: 1) Create a second access key in addition to the one in use. 2) Update all your applications to use the new access key and validate that the applications are working. 3) Change the state of the previous access key to inactive. 4) Validate that your applications are still working as expected. 5) Delete the inactive access key."
            }
        },
        {
            "Model":"Criterion",
            "Params":{
                "criterion_name":"IAM Access Key Rotation > 2 years",
                "criteria_provider_id":2,
                "invoke_class_name":"chalicelib.criteria.aws_iam_access_key_rotation.AwsIamAccessKeyRotationRed",
                "invoke_class_get_data_method": "describe_trusted_advisor_check_result",
                "title": "IAM Access Key Rotation Red",
                "description": "At least one active Identity and Access Management (IAM) access key has not been rotated in the last 2 years",
                "why_is_it_important": "Rotating IAM credentials periodically will significantly reduce the chances that a compromised set of access keys can be used without your knowledge to access certain components within your AWS account.",
                "how_do_i_fix_it": "Ensure that all your IAM user access keys are rotated at least every 90 days in order to decrease the likelihood of accidental exposures and protect your AWS resources against unauthorized access. To rotate access keys, it is recommended to follow these steps: 1) Create a second access key in addition to the one in use. 2) Update all your applications to use the new access key and validate that the applications are working. 3) Change the state of the previous access key to inactive. 4) Validate that your applications are still working as expected. 5) Delete the inactive access key."
            }
        },
        {
            "Model":"Criterion",
            "Params":{
                "criterion_name":"Potentially Exposed Key",
                "criteria_provider_id":2,
                "invoke_class_name":"chalicelib.criteria.aws_exposed_key.AwsIamPotentiallyExposedAccessKey",
                "invoke_class_get_data_method": "describe_trusted_advisor_check_result",
                "title": "Potentially Exposed Access Keys",
                "description": "An AWS Access Key ID and corresponding secret key were found on popular code repositories, or there is irregular EC2 usage that indicates that an access key has been compromised.",
                "why_is_it_important": "Access keys are what allow AWS users to authenticate themselves so that they can make use of certain functions within AWS, such as making API calls, or using the AWS command line interface to query the account, make or remove resources, and so on. If these access keys are leaked, attackers may gain a better understanding of how your account is structured, and they may steal and/or vandalise data within your account.",
                "how_do_i_fix_it": "Delete the affected access key, and generate a new one for the user or application. Please follow the below recommendations accordingly: - DELETE THE KEY (for IAM users): Navigate to your IAM Users list in the AWS Management Console, here: https://console.aws.amazon.com/iam/home#users . Please select the IAM user identified above. Click on the \"User Actions\" drop-down menu and then click \"Manage Access Keys\" to show that users active Access Keys. - ROTATE THE KEY (for applications) If your application uses the access key, you need to replace the exposed key with a new one. To do this, first create a second key (at that point both keys will be active) and modify your application to use the new key. Then disable (but do not delete) the first key. If there are any problems with your application, you can make the first key active again. When your application is fully functional with the first key inactive, please delete the first key. We strongly encourage you to immediately review your AWS account for any unauthorized AWS usage, suspect running instances, or inappropriate IAM users and policies. To review any unauthorized access, please inspect CloudTrail logs to see what was done with the access key while it was leaked and also Investigate how the access key was leaked, and take steps to prevent it from happening again."
            }
        },
        {
            "Model":"Criterion",
            "Params":{
                "criterion_name":"Suspected Exposed Key",
                "criteria_provider_id":2,
                "invoke_class_name":"chalicelib.criteria.aws_exposed_key.AwsIamSuspectedExposedAccessKey",
                "invoke_class_get_data_method": "describe_trusted_advisor_check_result",
                "title": "Suspected Exposed Access Keys",
                "description": "An AWS Access Key ID and corresponding secret key were found on popular code repositories, or there is irregular EC2 usage that indicates that an access key has been compromised.",
                "why_is_it_important": "Access keys are what allow AWS users to authenticate themselves so that they can make use of certain functions within AWS, such as making API calls, or using the AWS command line interface to query the account, make or remove resources, and so on. If these access keys are leaked, attackers may gain a better understanding of how your account is structured, and they may steal and/or vandalise data within your account.",
                "how_do_i_fix_it": "Alert not actionable."
            }
        }
    ]
  };

  var pipeline = gulp.src(config.files.environment_settings)
  .pipe(data(function(file) {
    var i;
    var function_name = "csw-"+env+"-database_create_items";
    var output_file = config.paths.environment + "/lambda.out"
    var working = config.paths.environment;

    return helpers.lambdaInvokePromise(function_name, working, payloads, file, output_file);
  }));


  return pipeline;

});

gulp.task('environment.database_build', gulp.series(
    'environment.database_create',
    'environment.database_create_tables',
    'environment.database_populate'
));
