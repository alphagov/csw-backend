/**
    This script creates a set of parameters shared across all deployed instances within an AWS account
    This means that all test and dev environments can share credentials but the live account has its own
 */
const gulp = require("gulp");
const data = require("gulp-data");
const modifyFile = require("gulp-modify-file");
const helpers = require(process.cwd() + "/gulp_helpers/helpers.js");

gulp.task("parameters.shared.google_auth", function() {
  // Load default settings
  var pipeline = gulp
    .src("../environments/example/settings.json")
    .pipe(
      modifyFile(function(content, path, file) {
        var defaults = JSON.parse(content);
        file.data = defaults;
        return content;
      })
    )
    .pipe(
      data(function(file) {
        // Ask user for environment name

        var name = "api_credentials";
        var prompt = "Please paste your Google OAuth credentials JSON file:";
        return helpers.promptInputPromise(name, prompt, file);
      })
    )
    .pipe(
      data(function(file) {
        // Upload api credentials to Parameter Store
        var name = "/" + file.data.tool + "/google/api-credentials";
        var property = "api_credentials";

        var region = file.data.region;
        return helpers.setParameterInPipelinePromise(
          name,
          file.data.api_credentials,
          region,
          file,
          property
        );
      })
    );

  return pipeline;
});

gulp.task("parameters.shared.terraform_states_bucket", function() {
  // Load default settings
  var pipeline = gulp
    .src("../environments/example/settings.json")
    .pipe(
      modifyFile(function(content, path, file) {
        var defaults = JSON.parse(content);
        file.data = defaults;
        return content;
      })
    )
    .pipe(
      data(function(file) {
        // Ask user for environment name

        var name = "bucket_name";
        var prompt = "Please paste your Terraform states S3 bucket name:";
        return helpers.promptInputPromise(name, prompt, file);
      })
    )
    .pipe(
      data(function(file) {
        // Upload api credentials to Parameter Store
        var name = "/" + file.data.tool + "/terraform/states-bucket";
        var property = "bucket_name";

        var region = file.data.region;
        return helpers.setParameterInPipelinePromise(
          name,
          file.data.bucket_name,
          region,
          file,
          property
        );
      })
    );

  return pipeline;
});

gulp.task(
  "parameters.shared",
  gulp.series(
    "parameters.shared.google_auth",
    "parameters.shared.terraform_states_bucket"
  )
);
