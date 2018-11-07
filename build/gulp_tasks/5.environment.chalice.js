const gulp = require('gulp');
const args = require('yargs').argv;
const data = require('gulp-data');
const modifyFile = require('gulp-modify-file');
const rename = require('gulp-rename');
const exec = require('child-process-promise').exec;
const awsParamStore = require('aws-param-store');
const AWS = require('aws-sdk');
const fs = require('fs');

console.log(process.cwd());
const helpers = require(process.cwd()+"/gulp_helpers/helpers.js");

// Store Chalice state file in S3 state bucket alongside Terraform tfstate.
// (after chalice deploy)
gulp.task('environment.chalice_s3_store_state', function() {

  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  var config = helpers.getConfigLocations(env, tool);

  var promise = gulp.src(config.files.chalice_deployed)
  .pipe(data(function(file) {
    // read env settings file into file.data
    file.data = JSON.parse(fs.readFileSync(config.files.environment_settings));
    return file.data;
  }))
  .pipe(data(function(file) {
    file.data.key = "staging/csw/chalice/"+env+".json";
    return file.data
  }))
  .pipe(modifyFile(function(content, path, file) {
    file.data.content = content;
    return content;
  }))
  .pipe(data(function(file) {
    console.log("Uploading " + file.data.key + " to " + file.data.bucket_name);
    var promise = helpers.s3UploadPromise(file);
    return promise;
  }));

  return promise;

});


// Retrieve Chalice state file from S3 and apply to chalice config folder
// (before chalice deploy)
gulp.task('environment.chalice_s3_retrieve_state', function() {

  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  var config = helpers.getConfigLocations(env, tool);

  var promise = gulp.src(config.files.environment_settings)
  .pipe(modifyFile(function(content, path, file) {
    file.data = JSON.parse(content);
  }))
  .pipe(data(function(file) {
    file.data.key = "staging/csw/chalice/"+env+".json";
    return file.data
  }))
  .pipe(data(function(file) {
    console.log("Downloading " + file.data.key + " from " + file.data.bucket_name);
    var promise = helpers.s3DownloadPromise(file);
    return promise;
  }))
  .pipe(data(function(file) {
    // if the S3 key doesn't exist (a new environment being deployed for the first time)
    // the s3DownloadPromise will return file.data.content as an empty string
    // in this case we need to create an empty chalice state file that
    if (!file.data.content || file.data.content == "") {
        file.data.content = JSON.stringify({
            "resources": [],
            "schema_version": "2.0",
            "backend": "api"
        }, null, 4);
    }
    return file.data;
  }))
  .pipe(modifyFile(function(content, path, file) {
    return file.data.content;
  }))
  .pipe(rename(env+".json"))
  .pipe(gulp.dest(config.paths.chalice_deployed));

  return promise;
});

// Remove Chalice state file from S3 bucket
// (after chalice delete)
gulp.task('environment.chalice_s3_delete_state', function() {

  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  var config = helpers.getConfigLocations(env, tool);

  var promise = gulp.src(config.files.environment_settings)
  .pipe(modifyFile(function(content, path, file) {
    file.data = JSON.parse(content);
  }))
  .pipe(data(function(file) {
    file.data.key = "staging/csw/chalice/"+env+".json";
    return file.data
  }))
  .pipe(data(function(file) {
    console.log("Deleting " + file.data.key + " from " + file.data.bucket_name);
    var promise = helpers.s3DeletePromise(file);
    return promise;
  }));

  return promise;
});

// TODO move the backup archived state file to S3
// Make a copy of the chalice state file in a folder named after the api gateway id.
// (after chalice deploy)
// Makes it easier to recover if something goes wrong and the chalice state file
// gets overwritten without being deleted first.
gulp.task('environment.chalice_archive_state', function() {

  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  var config = helpers.getConfigLocations(env, tool);

  var promise = gulp.src(config.files.chalice_deployed)
  .pipe(modifyFile(function(content, path, file) {
    file.data = JSON.parse(content);
    return content;
  }))
  .pipe(data(function(file) {
    var i, item;
    for (i in file.data.resources) {
        item = file.data.resources[i];
        if (item.name == "rest_api") {
            console.log(item);
            file.data.api_id = item.rest_api_id;
        }
    }

  }))
  .pipe(gulp.dest(function(file) {
    return config.paths.chalice_deployed + "/" + file.data.api_id;
  }));

  return promise;

});

// TODO move the backup archived state file to S3
// If chalice deploy / delete gets out of sync you can retrieve
// and delete the old state from the archived state file
gulp.task('environment.chalice_recover_state', function() {

  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;
  var state = (args.state == undefined)?'?':args.state;

  var config = helpers.getConfigLocations(env, tool);
  var archive_state = config.paths.chalice_deployed+"/"+state+"/"+env+".json";

  var promise = gulp.src(archive_state)
  .pipe(gulp.dest(config.paths.chalice_deployed));

  return promise;

});

// Generate chalice config file
// This task should only be run after environment.terraform_output
// which populates the terraform state variables into settings.json
gulp.task('environment.chalice_config', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  var config = helpers.getConfigLocations(env, tool);

  // Load default chalice config file

  var pipeline = gulp.src(config.files.default_chalice_config)
  .pipe(data(function(file) {
    // read env settings file into file.data
    file.data = JSON.parse(fs.readFileSync(config.files.environment_settings));
    console.log(file.data);
    return file.data;
  }))
  .pipe(data(function(file) {

    var parameter = '/csw/'+env+'/rds/user';
    var property = 'postgres_user_password';
    return helpers.getParameterInPipelinePromise(parameter, file.data.region, file, property);

  }))
  .pipe(modifyFile(function(content, path, file) {

    function renameProperty(object, oldName, newName) {
      object[newName] = object[oldName];
      delete(object[oldName]);
    }

    // set stage name = env
    file.data.config = JSON.parse(content);
    renameProperty(file.data.config.stages, '<env>', env);

    // set database credentials
    file.data.config.stages[env].environment_variables.CSW_ENV = file.data.environment;
    file.data.config.stages[env].environment_variables.CSW_PREFIX = file.data.prefix;
    file.data.config.stages[env].environment_variables.CSW_PASSWORD = file.data.postgres_user_password;
    file.data.config.stages[env].environment_variables.CSW_HOST = file.data.rds_connection_string;
    file.data.config.stages[env].environment_variables.CSW_REGION = file.data.region;

    var role_name = file.data.prefix+"_CstSecurityAgentRole"
    var role_arn = "arn:aws:iam::"+file.data.host_account_id+":role/"+role_name;
    file.data.config.stages[env].iam_role_arn = role_arn;
    var subnets = [
      file.data.public_subnet_1_id,
      file.data.public_subnet_2_id
    ];
    var security_groups = [
      file.data.public_security_group_id
    ];

    for (lambda in file.data.config.stages[env].lambda_functions) {
      console.log(lambda);
      file.data.config.stages[env].lambda_functions[lambda].subnet_ids = subnets;
      file.data.config.stages[env].lambda_functions[lambda].security_group_ids = security_groups;
    }

    file.data.content = JSON.stringify(file.data.config, null, 4);
    return file.data.content;
  }))
  .pipe(gulp.dest(config.paths.chalice_environment));

  return pipeline;
});

// Wrapper gulp task for chalice deploy command
gulp.task('environment.chalice_deploy', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 

  var config = helpers.getConfigLocations(env, tool);

  var pipeline = gulp.src(config.paths.chalice_environment)
  // symlink .chalice folder into csw-backend/chalice folder
  .pipe(gulp.symlink(config.paths.chalice_code))
  // execute the chalice deploy function for stage=env
  .pipe(data(function(file) {

    var task = 'chalice deploy --stage='+env;

    return helpers.runTaskInPipelinePromise(task, config.paths.chalice_code, file);
  }));

  return pipeline;

});

// Wrapper gulp task for chalice delete command
gulp.task('environment.chalice_delete', function() {
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var config = helpers.getConfigLocations(env, tool);

  var pipeline = gulp.src(config.paths.chalice_environment)
  // symlink .chalice folder into csw-backend/chalice folder
  .pipe(gulp.symlink(function() {
    console.log(config.paths.chalice_code);
    return config.paths.chalice_code;
  }))
  // execute the chalice deploy function for stage=env
  .pipe(data(function(file) {
    
    var task = 'chalice delete --stage='+env;

    return helpers.runTaskInPipelinePromise(task, config.paths.chalice_code, file);
  }));

  return pipeline;

});

// Perform full chalice initialisation and deploy
// including loading and saving state to S3.
gulp.task('environment.chalice_s3_deploy', gulp.series(
    'environment.chalice_config',
    'environment.chalice_s3_retrieve_state',
    'environment.chalice_deploy',
    'environment.chalice_archive_state',
    'environment.chalice_s3_store_state'
));

// Perform full chalice initialisation and delete
// including loading and saving state to S3.
gulp.task('environment.chalice_s3_delete', gulp.series(
    'environment.chalice_config',
    'environment.chalice_s3_retrieve_state',
    'environment.chalice_delete',
    'environment.chalice_s3_store_state'
));


