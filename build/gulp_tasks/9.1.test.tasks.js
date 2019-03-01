/**
    These tasks generate random secret data and upload to AWS SSM ParameterStore
    as encrypted parameters.

    Usage:
    gulp environment.e2e --env=dan --user=dan.jones
 */
const gulp = require('gulp');
const args = require('yargs').argv;
const data = require('gulp-data');
const modifyFile = require('gulp-modify-file');
const Input = require('prompt-input');
const randomstring = require('randomstring');
const AWS = require('aws-sdk');
const helpers = require(process.cwd()+"/gulp_helpers/helpers.js");

gulp.task('environment.test_rotate_credentials', function() {
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  var config = helpers.getConfigLocations(env, tool);

  // Load default settings
  var pipeline = gulp.src(config.files.environment_settings)
  .pipe(modifyFile(function(content, path, file) {
    var defaults = JSON.parse(content);
    file.data = defaults;
    file.data.config = config;
    return content;
  }))
  // Generate client id for e2e login page
  .pipe(data(function(file) {

    // create random token secret for JWTs.
    var client = randomstring.generate(20);
    process.env.CSW_CLIENT = client;
    var name = '/'+file.data.tool+'/'+env+'/credentials/tester/client';
    var property = 'client';
    var region = file.data.region;
    return helpers.setParameterInPipelinePromise(name, client, region, file, property);

  }))
  // Generate client secret for e2e login page
  .pipe(data(function(file) {

    // create random token secret for JWTs.
    var secret = randomstring.generate(256);
    process.env.CSW_SECRET = secret;
    var name = '/'+file.data.tool+'/'+env+'/credentials/tester/secret';
    var property = 'secret';
    var region = file.data.region;
    return helpers.setParameterInPipelinePromise(name, secret, region, file, property);

  }));
//  .pipe(data(function(file) {
//    console.log('environment', process.env);
//    return true;
//  }));
  return pipeline;

});

gulp.task('environment.test_disable_credentials', function() {
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  var config = helpers.getConfigLocations(env, tool);

  // Load default settings
  var pipeline = gulp.src(config.files.environment_settings)
  .pipe(modifyFile(function(content, path, file) {
    var defaults = JSON.parse(content);
    file.data = defaults;
    file.data.config = config;
    return content;
  }))
  // Generate client id for e2e login page
  .pipe(data(function(file) {

    // create random token secret for JWTs.
    var client = '[disabled]';
    process.env.CSW_CLIENT = client;
    var name = '/'+file.data.tool+'/'+env+'/credentials/tester/client';
    var property = 'client';
    var region = file.data.region;
    return helpers.setParameterInPipelinePromise(name, client, region, file, property);

  }))
//  .pipe(data(function(file) {
//    console.log('environment', process.env);
//    return true;
//  }));
  return pipeline;

});

gulp.task('environment.test_run_e2e', function() {
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;
  var user = (args.user == undefined)?'user':args.user;
  process.env.CSW_USER = user;

  var config = helpers.getConfigLocations(env, tool);

  // Load default settings
  var pipeline = gulp.src(config.files.environment_settings)
  .pipe(modifyFile(function(content, path, file) {
    var defaults = JSON.parse(content);
    file.data = defaults;
    file.data.config = config;
    return content;
  }))
  .pipe(data(function(file) {

    var task = 'behave';
    //var working = terraform_path+tool_path;
    var working = config.paths.root + "/chalice/e2e";

    return helpers.runTaskInPipelinePromise(task, working, file);

  }));

  return pipeline;

});

gulp.task('environment.e2e', gulp.series(
    'environment.test_rotate_credentials',
    'environment.test_run_e2e',
    'environment.test_rotate_credentials',
    'environment.test_disable_credentials'
));