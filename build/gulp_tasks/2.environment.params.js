const gulp = require('gulp');
const args = require('yargs').argv;
const data = require('gulp-data');
const modifyFile = require('gulp-modify-file');
const Input = require('prompt-input');
const randomstring = require('randomstring');
const AWS = require('aws-sdk');

gulp.task('environment.params', function() {
  var env = (args.env == undefined)?'test':args.env;
  // Load default settings
  var pipeline = gulp.src('../environments/'+env+'/settings.json')
  .pipe(modifyFile(function(content, path, file) {
    var defaults = JSON.parse(content);
    file.data = defaults;
    return content;
  }))
  // Generate token secret for JWT and upload to AWS Parameter Store
  .pipe(data(function(file) {

    // create random token secret for JWTs.
    var token = randomstring.generate(256);
    AWS.config.update({region: file.data.region});

    var ssm = new AWS.SSM({region: file.data.region});

    var params = {
      Name: '/'+file.data.tool+'/'+env+'/auth/token_secret',
      Type: 'SecureString',
      Value: token,
      Overwrite: true
    };

    var request = ssm.putParameter(params);
    var promise = request.promise()
    .then(function(data) {
      /* process the data */
      file.data.token = token;
      return file.data;
    },
    function(error) {
      /* handle the error */
      console.log('Failed to write token secret to parameter store');
      console.log(error);
      return file.data;
    });

    return promise;
  }))
  // Generate root password for RDS and upload to AWS Parameter Store
  .pipe(data(function(file) {

    // create random token secret for JWTs.
    var root_password = randomstring.generate(20);
    AWS.config.update({region: file.data.region});

    var ssm = new AWS.SSM({region: file.data.region});

    var params = {
      Name: '/'+file.data.tool+'/'+env+'/rds/root',
      Type: 'SecureString',
      Value: root_password,
      Overwrite: true
    };

    var request = ssm.putParameter(params);
    var promise = request.promise()
    .then(function(data) {
      /* process the data */
      file.data.root_password = root_password;
      return file.data;
    },
    function(error) {
      /* handle the error */
      console.log('Failed to write RDS password to parameter store');
      console.log(error);
      return file.data;
    })
  }))
  // Generate root password for RDS and upload to AWS Parameter Store
  .pipe(data(function(file) {

    // create random token secret for JWTs.
    var user_password = randomstring.generate(20);
    AWS.config.update({region: file.data.region});

    var ssm = new AWS.SSM({region: file.data.region});

    var params = {
      Name: '/'+file.data.tool+'/'+env+'/rds/user',
      Type: 'SecureString',
      Value: user_password,
      Overwrite: true
    };

    var request = ssm.putParameter(params);
    var promise = request.promise()
    .then(function(data) {
      /* process the data */
      file.data.user_password = user_password;
      return file.data;
    },
    function(error) {
      /* handle the error */
      console.log('Failed to write RDS password to parameter store');
      console.log(error);
      return file.data;
    });

    return promise;
  }))

  return pipeline;

});