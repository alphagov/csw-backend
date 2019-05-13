const gulp = require("gulp");
const args = require("yargs").argv;
const data = require("gulp-data");
const modifyFile = require("gulp-modify-file");
const rename = require("gulp-rename");
const helpers = require(process.cwd() + "/gulp_helpers/helpers.js");

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
        var content = "";

        for (varName in file.data) {
          varValue = file.data[varName];
          switch (varValue) {
            case "true":
            case true:
            case "false":
            case false:
              {
                content += varName + " = " + varValue + "\n";
              }
              break;
            default:
              {
                content += varName + ' = "' + varValue + '"\n';
              }
              break;
          }
        }

        console.log(content);
        file.data.content = content;
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
        // sanitize
        var keep = ["api_gateway_url"];

        file.data = helpers.removeExceptPropertiesInPipeline(file.data, keep);
        return file.data;
      })
    )
    .pipe(
      data(function(file) {
        var content = "";

        for (varName in file.data) {
          varValue = file.data[varName];
          switch (varValue) {
            case "true":
            case true:
            case "false":
            case false:
              {
                content += varName + " = " + varValue + "\n";
              }
              break;
            default:
              {
                content += varName + ' = "' + varValue + '"\n';
              }
              break;
          }
        }

        console.log(content);
        file.data.content = content;
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
  gulp.series("environment.cloudfront_backend.tfvars", "environment.cloudfront_apply.tfvars")
);
