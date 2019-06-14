const gulp = require("gulp");
const args = require("yargs").argv;
const data = require("gulp-data");
const modifyFile = require("gulp-modify-file");
const rename = require("gulp-rename");
const helpers = require(process.cwd() + "/gulp_helpers/helpers.js");
const fs = require("fs");

gulp.task("environment.cloudfront_backend.tfvars", function() {
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
        // sanitize
        file.data.bucket = "" + file.data.bucket_name;
        file.data.key = "staging/csw/cloudfront/" + env + ".tfstate";
        file.data.encrypt = true;
        var keep = ["region", "bucket", "key", "encrypt"];

        file.data = helpers.removeExceptPropertiesInPipeline(file.data, keep);
        return file.data;
      })
    )
    .pipe(
      data(function(file) {
        file.data.content = helpers.getVarFileContent(file);
        return file.data;
      })
    )
    .pipe(
      modifyFile(function(content, path, file) {
        return file.data.content;
      })
    )
    .pipe(rename("backend.tfvars"))
    .pipe(
      gulp.dest(function(file) {
        var target = "../environments/" + env + "/terraform/cloudfront";
        console.log(target);
        return target;
      })
    );

  return pipeline;
});

gulp.task("environment.cloudfront_apply.tfvars", function() {
  var env = args.env == undefined ? "test" : args.env;
  var tool = args.tool == undefined ? "csw" : args.tool;
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
        file.data.env = env;
        return content;
      })
    )
    .pipe(
      data(function(file) {
        file.data.resources.forEach(function(resource) {
          if (resource.name == "rest_api") {
            file.data.api_gateway_url = resource.rest_api_url;

            console.log(resource.rest_api_url);
          }
        });
        return file.data;
      })
    )
    .pipe(
      data(function(file) {
        let settingsFile = file.data.config.files.environment_settings;
        let settingsData = fs.readFileSync(settingsFile);
        file.data.settings = JSON.parse(settingsData);
        file.data.region = file.data.settings.region;
      })
    )
    .pipe(
      data(function(file) {
        return helpers.getDomainSettings(file);
      })
    )
    .pipe(
      data(function(file) {
        // sanitize
        var keep = [
          "region",
          "env",
          "dns_zone_fqdn",
          "sub_domain",
          "api_gateway_url"
        ];

        file.data = helpers.removeExceptPropertiesInPipeline(file.data, keep);
        return file.data;
      })
    )
    .pipe(
      data(function(file) {
        file.data.content = helpers.getVarFileContent(file);
        return file.data;
      })
    )
    .pipe(
      modifyFile(function(content, path, file) {
        return file.data.content;
      })
    )
    .pipe(rename("apply.tfvars"))
    .pipe(
      gulp.dest(function(file) {
        var target = "../environments/" + env + "/terraform/cloudfront";
        console.log(target);
        return target;
      })
    );
  return pipeline;
});

gulp.task(
  "environment.cloudfront_tfvars",
  gulp.series(
    "environment.cloudfront_backend.tfvars",
    "environment.cloudfront_apply.tfvars"
  )
);

gulp.task("environment.cloudfront_terraform_init", function() {
  var env = args.env == undefined ? "test" : args.env;
  var tool = args.tool == undefined ? "csw" : args.tool;

  var config = helpers.getConfigLocations(env, tool);
  console.log(config);

  // Load default settings
  var pipeline = gulp
    .src("./node_modules/csw-infra")
    .pipe(gulp.symlink(config.paths.terraform))
    .pipe(
      data(function(file) {
        var task =
          "terraform init -backend-config=" +
          config.paths.terraform +
          "/cloudfront/backend.tfvars -reconfigure";
        //var working = terraform_path+tool_path;
        var working = config.paths.terraform_tool_cloudfront;

        return helpers.runTaskInPipelinePromise(task, working, file);
      })
    );

  return pipeline;
});

gulp.task("environment.cloudfront_terraform_output", function() {
  var env = args.env == undefined ? "test" : args.env;
  var tool = args.tool == undefined ? "csw" : args.tool;
  var config = helpers.getConfigLocations(env, tool);

  // Load settings file
  var pipeline = gulp
    .src(config.files.environment_settings)
    .pipe(
      modifyFile(function(content, path, file) {
        var defaults = JSON.parse(content);
        file.data = defaults;
        return content;
      })
    )
    // Get terraform output and add to file.data
    .pipe(
      data(function(file) {
        //var working = terraform_path+tool_path;
        var working = config.paths.terraform_tool;

        var promise = helpers.getTerraformOutputInPipelinePromise(
          working,
          file
        );

        return promise;
      })
    )
    .pipe(
      modifyFile(function(content, path, file) {
        return JSON.stringify(file.data, null, 4);
      })
    )
    .pipe(gulp.dest(config.paths.environment));

  return pipeline;
});

gulp.task("environment.cloudfront_terraform_plan", function() {
  var env = args.env == undefined ? "test" : args.env;
  var tool = args.tool == undefined ? "csw" : args.tool;
  var config = helpers.getConfigLocations(env, tool);

  // Load settings file
  var pipeline = gulp
    .src(config.files.environment_settings)
    .pipe(
      modifyFile(function(content, path, file) {
        var defaults = JSON.parse(content);
        file.data = defaults;
        return content;
      })
    )
    .pipe(
      data(function(file) {
        var task =
          "terraform plan -var-file=" +
          config.paths.terraform +
          "/cloudfront/apply.tfvars";
        //var working = terraform_path+tool_path;
        var working = config.paths.terraform_tool_cloudfront;

        return helpers.runTaskInPipelinePromise(task, working, file);
      })
    );

  return pipeline;
});

gulp.task("environment.cloudfront_terraform_apply", function() {
  var env = args.env == undefined ? "test" : args.env;
  var tool = args.tool == undefined ? "csw" : args.tool;
  var config = helpers.getConfigLocations(env, tool);

  // Load settings file
  var pipeline = gulp
    .src(config.files.environment_settings)
    .pipe(
      modifyFile(function(content, path, file) {
        var defaults = JSON.parse(content);
        file.data = defaults;
        return content;
      })
    )
    .pipe(
      data(function(file) {
        var task =
          "terraform apply -var-file=" +
          config.paths.terraform +
          "/cloudfront/apply.tfvars" +
          " -auto-approve";
        //var working = terraform_path+tool_path;
        var working = config.paths.terraform_tool_cloudfront;

        return helpers.runTaskInPipelinePromise(task, working, file);
      })
    );
  return pipeline;
});

gulp.task("environment.cloudfront_terraform_destroy", function() {
  var env = args.env == undefined ? "test" : args.env;
  var tool = args.tool == undefined ? "csw" : args.tool;
  var config = helpers.getConfigLocations(env, tool);

  // Load settings file
  var pipeline = gulp
    .src(config.files.environment_settings)
    .pipe(
      modifyFile(function(content, path, file) {
        var defaults = JSON.parse(content);
        file.data = defaults;
        return content;
      })
    )
    .pipe(
      data(function(file) {
        var task =
          "terraform destroy -var-file=" +
          config.paths.terraform +
          "/cloudfront/apply.tfvars" +
          " -auto-approve";
        //var working = terraform_path+tool_path;
        var working = config.paths.terraform_tool_cloudfront;

        return helpers.runTaskInPipelinePromise(task, working, file);
      })
    );
  return pipeline;
});

gulp.task("environment.cloudfront_terraform_push", function() {
  var env = args.env == undefined ? "test" : args.env;
  var tool = args.tool == undefined ? "csw" : args.tool;
  var config = helpers.getConfigLocations(env, tool);

  // Load settings file
  var pipeline = gulp
    .src(config.files.environment_settings)
    .pipe(
      modifyFile(function(content, path, file) {
        var defaults = JSON.parse(content);
        file.data = defaults;
        return content;
      })
    )
    .pipe(
      data(function(file) {
        var task = "terraform state push errored.tfstate";
        //var working = terraform_path+tool_path;
        var working = config.paths.terraform_tool_cloudfront;

        return helpers.runTaskInPipelinePromise(task, working, file);
      })
    );
  return pipeline;
});
