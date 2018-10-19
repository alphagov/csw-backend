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
    // Get Google API Console OAuth credentials file from AWS SSM Parameter Store 
    .pipe(data(function(file) {

      var promise = awsParamStore.getParameter( '/csw/google/api-credentials', { region: file.data.region })

      promise.then(function(parameter) {
        file.data.google_creds = parameter.Value.replace(/\"/g,"'");
        return file.data;
      });

      return promise;
    }))
    // Get Terraforms state S3 bucket name from AWS SSM Parameter Store
    .pipe(data(function(file) {

      var promise = awsParamStore.getParameter( '/csw/terraform/states-bucket', { region: file.data.region })
      .then(function(parameter) {
        file.data.bucket_name = parameter.Value;
        return file.data;
      });

      return promise;
    }))
    // Ask user for host AWS account ID. 
    .pipe(data(function(file) {

      var input = new Input({
        name: 'host_account',
        message: 'Please enter the hosting AWS account ID:'
      });

      var promise = input.run()
      .then(function(answer) {
        console.log(answer);
        // TODO validate answer format
        file.data.host_account= answer;
      });

      return promise;
    }))
    // Ask user for environment name 
    .pipe(data(function(file) {

      var input = new Input({
        name: 'environment',
        message: 'Please enter the environment name:'
      });

      var promise = input.run()
      .then(function(answer) {
        console.log(answer);
        // TODO validate answer format
        file.data.environment= answer;
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
        'host_account',
        'google_creds',
        'bucket_name'
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