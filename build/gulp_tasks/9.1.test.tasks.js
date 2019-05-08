/**
    These tasks generate random secret data and upload to AWS SSM ParameterStore
    as encrypted parameters.

    Usage:
    gulp environment.e2e --env=dan --user=dan.jones
 */
const gulp = require("gulp");
const args = require("yargs").argv;
const data = require("gulp-data");
const modifyFile = require("gulp-modify-file");
const Input = require("prompt-input");
const randomstring = require("randomstring");
const AWS = require("aws-sdk");
const helpers = require(process.cwd() + "/gulp_helpers/helpers.js");

gulp.task("environment.test_setup", function() {
  var env = args.env == undefined ? "test" : args.env;
  var tool = args.tool == undefined ? "csw" : args.tool;
  var user = args.user == undefined ? "user" : args.user;
  var headless =
    args.headless == undefined
      ? true // default to headless if argument not specified
      : helpers.parseBooleanArgument(args.headless);
  process.env.CSW_USER = user;
  process.env.CSW_E2E_HEADLESS = headless;

  var config = helpers.getConfigLocations(env, tool);
  console.log(config.files.chalice_deployed);
  // Load chalice deployment
  var pipeline = gulp
    .src(config.files.chalice_deployed)
    .pipe(
      modifyFile(function(content, path, file) {
        var deployed = JSON.parse(content);
        file.data = deployed;
        file.data.config = config;
        return content;
      })
    )
    .pipe(
      data(function(file) {
        file.data.resources.forEach(function(resource) {
          if (resource.name == "rest_api") {
            process.env.CSW_URL = resource.rest_api_url;
            console.log(resource.rest_api_url);
          }
        });
      })
    );
  return pipeline;
});

gulp.task("environment.test_rotate_credentials", function() {
  var env = args.env == undefined ? "test" : args.env;
  var tool = args.tool == undefined ? "csw" : args.tool;
  var config = helpers.getConfigLocations(env, tool);

  // Load default settings
  var pipeline = gulp
    .src(config.files.environment_settings)
    .pipe(
      modifyFile(function(content, path, file) {
        var defaults = JSON.parse(content);
        file.data = defaults;
        file.data.config = config;
        return content;
      })
    )
    // Generate client id for e2e login page
    .pipe(
      data(function(file) {
        // create random token secret for JWTs.
        var client = randomstring.generate(20);
        process.env.CSW_CLIENT = client;
        var name =
          "/" + file.data.tool + "/" + env + "/credentials/tester/client";
        var property = "client";
        var region = file.data.region;
        return helpers.setParameterInPipelinePromise(
          name,
          client,
          region,
          file,
          property
        );
      })
    )
    // Generate client secret for e2e login page
    .pipe(
      data(function(file) {
        // create random token secret for JWTs.
        var secret = randomstring.generate(256);
        process.env.CSW_SECRET = secret;
        var name =
          "/" + file.data.tool + "/" + env + "/credentials/tester/secret";
        var property = "secret";
        var region = file.data.region;
        return helpers.setParameterInPipelinePromise(
          name,
          secret,
          region,
          file,
          property
        );
      })
    );
  //  .pipe(data(function(file) {
  //    console.log('environment', process.env);
  //    return true;
  //  }));
  return pipeline;
});

gulp.task("environment.test_disable_credentials", function() {
  var env = args.env == undefined ? "test" : args.env;
  var tool = args.tool == undefined ? "csw" : args.tool;

  var config = helpers.getConfigLocations(env, tool);

  // Load default settings
  var pipeline = gulp
    .src(config.files.environment_settings)
    .pipe(
      modifyFile(function(content, path, file) {
        var defaults = JSON.parse(content);
        file.data = defaults;
        file.data.config = config;
        return content;
      })
    )
    // Generate client id for e2e login page
    .pipe(
      data(function(file) {
        // create random token secret for JWTs.
        var client = "[disabled]";
        process.env.CSW_CLIENT = client;
        var name =
          "/" + file.data.tool + "/" + env + "/credentials/tester/client";
        var property = "client";
        var region = file.data.region;
        return helpers.setParameterInPipelinePromise(
          name,
          client,
          region,
          file,
          property
        );
      })
    );
  return pipeline;
});

gulp.task("environment.test_run_e2e", function() {
  var env = args.env == undefined ? "test" : args.env;
  var tool = args.tool == undefined ? "csw" : args.tool;

  var config = helpers.getConfigLocations(env, tool);

  // Load default settings
  var pipeline = gulp
    .src(config.files.environment_settings)
    .pipe(
      modifyFile(function(content, path, file) {
        var defaults = JSON.parse(content);
        file.data = defaults;
        file.data.config = config;
        return content;
      })
    )
    .pipe(
      data(function(file) {
        var task = "behave";
        //var working = terraform_path+tool_path;
        var working = config.paths.root + "/chalice/e2e";

        return helpers.runTaskInPipelinePromise(task, working, file);
      })
    )
    .pipe(
      data(function(file) {
        console.log("Exit status: ", file.data.exit_status);
        process.env.EXIT_STATUS = file.data.exit_status;
      })
    );

  return pipeline;
});

// We don't want to signal failure when the tests fail
// since this would break the credentials management
// instead we want to run to the end of the process
// and then fail the overall gulp task.
// It seems there's no nice way to set the exit status
// so I've added this final task which triggers
// process.exit() if there was a failure which sets the
// exit status (echo $?) to 1
gulp.task("environment.test_e2e_report_status", done => {
  if (process.env.EXIT_STATUS == 1) {
    console.log("Failed: A non-zero exit status was reported");
    done(new Error("Failed: A non-zero exit status was reported"));
  } else {
    done();
  }
});

gulp.task(
  "environment.e2e",
  gulp.series(
    "environment.test_setup",
    "environment.test_rotate_credentials",
    "environment.test_run_e2e",
    "environment.test_rotate_credentials",
    "environment.test_disable_credentials",
    "environment.test_e2e_report_status"
  )
);
