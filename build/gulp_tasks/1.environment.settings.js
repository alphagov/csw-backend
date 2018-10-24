const gulp = require('gulp');
const args = require('yargs').argv;
const data = require('gulp-data');
const modifyFile = require('gulp-modify-file');
const awsParamStore = require('aws-param-store');
const Input = require('prompt-input');
const AWS = require('aws-sdk');
const helpers = require(process.cwd()+"/gulp_helpers/helpers.js");

gulp.task('environment.settings', function() {

  // Load default settings
  var pipeline = gulp.src('../environments/example/settings.json')
  .pipe(modifyFile(function(content, path, file) {
    var defaults = JSON.parse(content);
    file.data = defaults;
    return content;
  }))
  .pipe(data(function(file) {
    // Get Google API Console OAuth credentials file from AWS SSM Parameter Store
    console.log("Get Google API Credentials");

    var promise = awsParamStore.getParameter( '/csw/google/api-credentials', { region: file.data.region })

    promise.then(function(parameter) {
      file.data.google_creds = parameter.Value.replace(/\"/g,'\"');
      return file.data;
    });

    return promise;
  }))
  .pipe(data(function(file) {
    // Get Terraforms state S3 bucket name from AWS SSM Parameter Store
    console.log("Get terraform states bucket");

    var parameter = '/csw/terraform/states-bucket';
    var property = 'bucket_name';
    var region = file.data.region;
    return helpers.getParameterInPipelinePromise(parameter, region, file, property)
  }))
  // Read host account ID using STS GetCallerIdentity
  .pipe(data(function(file) {
    
    return helpers.getAwsAccountIdPromise()
    .then(function(accountId) {
      file.data.host_account_id = accountId;
    });

  }))
  .pipe(data(function(file) {
    // Ask user for environment name

    var name = 'environment';
    var prompt = 'Please enter the environment name:';
    return helpers.promptInputPromise(name, prompt, file);
  }))
  .pipe(data(function(file) {
    // Ask user for an IP prefix
    
    var name = 'ip_16bit_prefix';
    var prompt = 'Please enter the the first 2 numbers of the IP range (eg 10.x):';
    return helpers.promptInputPromise(name, prompt, file);
  }))
  .pipe(data(function(file) {
    // Ask user for an SSH key name

    var name = 'ssh_key_name';
    var prompt = 'Please enter the name of an existing AWS ssh key:';
    return helpers.promptInputPromise(name, prompt, file);
  }))
  .pipe(data(function(file) {
    // Ask the path to the public ssh key described above

    var name = 'ssh_public_key_path';
    var prompt = 'Please enter the path to the ssh public key file:';
    return helpers.promptInputPromise(name, prompt, file);
  }))
  .pipe(data(function(file) {

    // sanitize any unexpected extra paramters from AWS response
    var expected = [
      'region',
      'tool',
      'environment',
      'prefix',
      'host_account_id',
      'google_creds',
      'bucket_name',
      'ip_16bit_prefix',
      'ssh_key_name',
      'ssh_public_key_path'
    ];
    /*
    for (item in file.data) {
      if (expected.indexOf(item) < 0) {
        delete file.data[item];
      }
    }
    */
    file.data = helpers.removeExceptPropertiesInPipeline(file.data, expected);
    file.data.prefix = file.data.tool + '-' + file.data.environment;

    return file.data;

  }))
  .pipe(modifyFile(function(content, path, file){
    return JSON.stringify(file.data, null, 4);
  }))
  //.pipe(rename("settings.json"))
  .pipe(gulp.dest(function(file) {
    return "../environments/"+file.data.environment;
  }))
  return pipeline;

});