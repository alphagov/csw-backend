const gulp = require('gulp');
const args = require('yargs').argv;
const data = require('gulp-data');
const modifyFile = require('gulp-modify-file');
const Input = require('prompt-input');
const randomstring = require('randomstring');
const AWS = require('aws-sdk');
const helpers = require(process.cwd()+"/gulp_helpers/helpers.js");

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
    var name = '/'+file.data.tool+'/'+env+'/auth/token_secret';
    var property = 'token';
    var region = file.data.region;
    return helpers.setParameterInPipelinePromise(name, token, region, file, property);

  }))
  // Generate root password for RDS and upload to AWS Parameter Store
  .pipe(data(function(file) {

    // create random token secret for JWTs.
    var root_password = randomstring.generate(20);
    var name = '/'+file.data.tool+'/'+env+'/rds/root';
    var property = 'root_password';
    var region = file.data.region;
    return helpers.setParameterInPipelinePromise(name, root_password, region, file, property);
    
  }))
  // Generate root password for RDS and upload to AWS Parameter Store
  .pipe(data(function(file) {

    // create random token secret for JWTs.
    var user_password = randomstring.generate(20);
    var name = '/'+file.data.tool+'/'+env+'/rds/user';
    var property = 'user_password';
    var region = file.data.region;
    return helpers.setParameterInPipelinePromise(name, user_password, region, file, property);

  }))

  return pipeline;

});