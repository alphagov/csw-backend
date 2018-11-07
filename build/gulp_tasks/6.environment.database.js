/**
  Create database, user, define schema and populate.
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
  var pipeline = gulp.src(config.files.settings)
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

  var pipeline = gulp.src(config.files.settings)
  // Read settings into file.data
  .pipe(modifyFile(function(content, path, file) {
    var settings = JSON.parse(content);
    file.data = settings;
    return content;
  }))
  .pipe(data(function(file) {

    var payload = {
        "Tables":[
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
                "how_do_i_fix_it": "In almost all cases, SSH ingress should be limited to the <a target=\"gds-wiki\" href=\"https://sites.google.com/a/digital.cabinet-office.gov.uk/gds-internal-it/news/aviationhouse-sourceipaddresses\">GDS public IPs</a>. There may be exceptions where we are working closely in partnership with another organisation."
            }
        },
        {
            "Model":"Criterion",
            "Params":{
                "criterion_name":"Security Groups - SSH ingress open for flagged ports",
                "criteria_provider_id":2,
                "invoke_class_name":"chalicelib.criteria.aws_ec2_security_group_ingress_open.AwsEc2SecurityGroupIngressOpen",
                "invoke_class_get_data_method": "describe_security_groups",
                "title": "Security Groups - SSH ingress open for flagged ports",
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
        }
    ]
  };

  var pipeline = gulp.src(config.files.settings)
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
