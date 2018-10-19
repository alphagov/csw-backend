const gulp = require('gulp');
var modifyFile = require('gulp-modify-file');
var data = require('gulp-data');
var awsParamStore = require('aws-param-store');
var Input = require('prompt-input');

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
      file.data.google_creds = parameter.Value.replace(/\"/g,"'");
      return file.data;
    });

    return promise;
  }))
  .pipe(data(function(file) {
    // Get Terraforms state S3 bucket name from AWS SSM Parameter Store
    console.log("Get terraform states bucket");

    var promise = awsParamStore.getParameter( '/csw/terraform/states-bucket', { region: file.data.region })
    .then(function(parameter) {
      file.data.bucket_name = parameter.Value;
      return file.data;
    });

    return promise;
  }))
  .pipe(data(function(file) {
    // Ask user for host AWS account ID.

    var input = new Input({
      name: 'host_account_id',
      message: 'Please enter the hosting AWS account ID:'
    });

    var promise = input.run()
    .then(function(answer) {
      console.log(answer);
      // TODO validate answer format
      file.data.host_account_id = answer;
    });

    return promise;
  }))
  .pipe(data(function(file) {
    // Ask user for environment name

    var input = new Input({
      name: 'environment',
      message: 'Please enter the environment name:'
    });

    var promise = input.run()
    .then(function(answer) {
      console.log(answer);
      // TODO validate answer format
      file.data.environment = answer;
    });

    return promise;
  }))
  .pipe(data(function(file) {
    // Ask user for an IP prefix

    var input = new Input({
      name: 'ip_16bit_prefix',
      message: 'Please enter the the first 2 numbers of the IP range (eg 10.x):'
    });

    var promise = input.run()
    .then(function(answer) {
      console.log(answer);
      // TODO validate answer format
      file.data.ip_16bit_prefix = answer;
    });

    return promise;
  }))
  .pipe(data(function(file) {
    // Ask user for an SSH key name

    var input = new Input({
      name: 'ssh_key_name',
      message: 'Please enter the name of an existing AWS ssh key:'
    });

    var promise = input.run()
    .then(function(answer) {
      console.log(answer);
      // TODO validate answer format
      file.data.ssh_key_name = answer;
    });

    return promise;
  }))
  .pipe(data(function(file) {
    // Ask the path to the public ssh key described above

    var input = new Input({
      name: 'ssh_public_key_path',
      message: 'Please enter the path to the ssh public key file:'
    });

    var promise = input.run()
    .then(function(answer) {
      console.log(answer);
      // TODO validate answer format
      file.data.ssh_public_key_path = answer;
    });

    return promise;
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

    for (item in file.data) {
      if (expected.indexOf(item) < 0) {
        delete file.data[item];
      }
    }
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