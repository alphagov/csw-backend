/**
  Create database, user, define schema and populate with default data.

  This doesn't create any product teams or account subscriptions
*/
const gulp = require("gulp");
const args = require("yargs").argv;
const data = require("gulp-data");
const modifyFile = require("gulp-modify-file");
const exec = require("child-process-promise").exec;
const awsParamStore = require("aws-param-store");
const fs = require("fs");

console.log(process.cwd());
const helpers = require(process.cwd() + "/gulp_helpers/helpers.js");

gulp.task("environment.database_create", function() {
  var env = args.env == undefined ? "test" : args.env;
  var tool = args.tool == undefined ? "csw" : args.tool;

  var config = helpers.getConfigLocations(env, tool);

  // Load settings file
  var pipeline = gulp
    .src(config.files.environment_settings)
    // Parse settings into file.data
    .pipe(
      modifyFile(function(content, path, file) {
        var settings = JSON.parse(content);
        file.data = settings;
        return content;
      })
    )
    // Get RDS root password from parameter store
    // Add to file.data
    .pipe(
      data(function(file) {
        var parameter = "/csw/" + env + "/rds/root";
        var property = "postgres_root_password";
        return helpers.getParameterInPipelinePromise(
          parameter,
          file.data.region,
          file,
          property
        );
      })
    )
    // Get RDS user password from parameter store
    // Add to file.data
    .pipe(
      data(function(file) {
        var parameter = "/csw/" + env + "/rds/user";
        var property = "postgres_user_password";
        return helpers.getParameterInPipelinePromise(
          parameter,
          file.data.region,
          file,
          property
        );
      })
    )
    // Pass commands to psql_tunnel.py script
    .pipe(
      data(function(file) {
        path = config.paths.root + "/build/gulp_helpers";

        command = "CREATE DATABASE " + file.data.tool + ";";

        var promise = helpers
          .psqlExecuteInPipelinePromise(path, command, file)
          .then(function(output) {
            var command =
              "CREATE USER cloud_sec_watch WITH ENCRYPTED PASSWORD '" +
              file.data.postgres_user_password +
              "';";
            return helpers.psqlExecuteInPipelinePromise(path, command, file);
          })
          .then(function(output) {
            var command =
              "GRANT ALL PRIVILEGES ON DATABASE csw TO cloud_sec_watch;";
            return helpers.psqlExecuteInPipelinePromise(path, command, file);
          });

        return promise;
      })
    );

  return pipeline;
});

gulp.task("environment.database_switch_config", function() {
  var env = args.env == undefined ? "test" : args.env;
  var tool = args.tool == undefined ? "csw" : args.tool;

  var config = helpers.getConfigLocations(env, tool);
  // TODO - check path exists before trying to symlink
  // if (fs.existsSync(sqlPath)) {
  var pipeline = gulp
    .src(
      config.paths.root +
        "/../csw-configuration/environments/" +
        env +
        "/sql/population"
    )
    .pipe(gulp.symlink(config.paths.root + "/build/sql"));

  return pipeline;
});

gulp.task("environment.database_run_migrations", function() {
  var env = args.env == undefined ? "test" : args.env;
  var tool = args.tool == undefined ? "csw" : args.tool;

  var config = helpers.getConfigLocations(env, tool);
  var pipeline = gulp
    .src(config.files.environment_settings)
    // Parse settings into file.data
    .pipe(
      modifyFile(function(content, path, file) {
        var settings = JSON.parse(content);
        file.data = settings;
        return content;
      })
    )
    // Get RDS user password from parameter store
    // Add to file.data
    .pipe(
      data(function(file) {
        var parameter = "/csw/" + env + "/rds/user";
        var property = "postgres_user_password";
        return helpers.getParameterInPipelinePromise(
          parameter,
          file.data.region,
          file,
          property
        );
      })
    )
    // Pass commands to psql_tunnel.py script
    .pipe(
      data(function(file) {
        var promise, path, command, meta_table;

        meta_table = "public._metadata_version";
        path = config.paths.root + "/build/gulp_helpers";

        command = "SELECT * FROM " + meta_table + ";";

        promise = helpers.psqlExecuteInPipelinePromise(
          path,
          command,
          file,
          "cloud_sec_watch",
          file.data.postgres_user_password,
          "csw"
        );

        promise
          .then(function(output) {
            var type, current_level, apply;

            //console.log(file.data.task_output);
            try {
              output = JSON.parse(file.data.task_output);
            } catch (err) {
              /*
            The assumption here is that there are 2 indices for migrations
            1. definition - Schema creates and alters.
            2. population - My plan is to retrieve these files from a separate private repository
                which can contain all the GDS specific configuration data about teams we've
                onboarded. This should replace the need for the database populate gulp task
            */
              output = [["definition", 0], ["population", 0]];
            }

            file.data.database = {};
            let scriptList = [];
            // For each type get the list of scripts and compare the the current index
            output.forEach(function(row) {
              type = row[0];
              currentLevel = row[1];
              file.data.database[type] = currentLevel;
              let sqlPath = config.paths.root + "/build/sql/" + type;
              // Ensure the folder exists before trying to read it
              if (fs.existsSync(sqlPath)) {
                // Get list of matching files
                let items = fs.readdirSync(sqlPath);
                // Iterate across list and compare to current index
                items.forEach(function(item) {
                  let index = parseInt(item.replace(/\.sql/, ""));
                  // If the migration is later than the current index add to list.
                  if (index > currentLevel) {
                    let script = {
                      type: type,
                      script: item
                    };
                    scriptList.push(script);
                  }
                });
              }
            });
            return scriptList;
          })
          .then(function(scriptList) {
            // Use a reduce to force the list of promises to chain after
            // each other rather than all chaining onto the first promise
            // First create a resolved promise to chain everything else onto
            var promise = Promise.resolve();
            scriptList.reduce(function(previousPromise, item) {
              let sqlPath = config.paths.root + "/build/sql/" + item.type;
              let index = parseInt(item.script.replace(/\.sql/, ""));
              // After the promise passed in from reduce
              return previousPromise
                .then(function() {
                  let scriptPath = sqlPath + "/" + item.script;
                  // Execute the script through the tunnel script
                  return helpers.psqlExecuteScriptInPipelinePromise(
                    path,
                    scriptPath,
                    file,
                    "cloud_sec_watch",
                    file.data.postgres_user_password,
                    "csw"
                  );
                  // After the script has executed update the index in the _metadata_version table
                })
                .then(function() {
                  let command =
                    "UPDATE " +
                    meta_table +
                    " SET version = " +
                    index +
                    " WHERE type='" +
                    item.type +
                    "'";
                  return helpers.psqlExecuteInPipelinePromise(
                    path,
                    command,
                    file,
                    "cloud_sec_watch",
                    file.data.postgres_user_password,
                    "csw"
                  );
                });
            }, promise); // pass in the resolved promise to start
          });
        return promise;
      })
    );

  return pipeline;
});

gulp.task(
  "environment.database_migrate",
  gulp.series(
    "environment.database_switch_config",
    "environment.database_run_migrations"
  )
);

gulp.task("environment.database_define_criteria", function() {
  var env = args.env == undefined ? "test" : args.env;
  var tool = args.tool == undefined ? "csw" : args.tool;

  var config = helpers.getConfigLocations(env, tool);

  var pipeline = gulp.src(config.files.environment_settings).pipe(
    data(function(file) {
      var i;
      var function_name = "csw-" + env + "-database_add_new_criteria";
      var output_file = config.paths.environment + "/lambda.out";
      var working = config.paths.environment;

      return helpers.lambdaInvokePromise(
        function_name,
        working,
        null,
        file,
        output_file
      );
    })
  );

  return pipeline;
});

gulp.task(
  "environment.database_build",
  gulp.series("environment.database_create", "environment.database_migrate")
);
