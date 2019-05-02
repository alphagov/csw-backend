/**
  Create database, user, define schema and populate with default data.

  This doesn't create any product teams or account subscriptions
*/
const gulp = require('gulp');
const args = require('yargs').argv;
const data = require('gulp-data');
const modifyFile = require('gulp-modify-file');
const exec = require('child-process-promise').exec;
const awsParamStore = require('aws-param-store');
const fs = require('fs');

console.log(process.cwd());
const helpers = require(process.cwd()+"/gulp_helpers/helpers.js");

gulp.task('environment.database_create', function() {

  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  var config = helpers.getConfigLocations(env, tool);

  // Load settings file
  var pipeline = gulp.src(config.files.environment_settings)
  // Parse settings into file.data
  .pipe(modifyFile(function(content, path, file) {
    var settings = JSON.parse(content);
    file.data = settings;
    return content;
  }))
  // Get RDS root password from parameter store
  // Add to file.data
  .pipe(data(function(file) {

    var parameter = '/csw/'+env+'/rds/root';
    var property = 'postgres_root_password';
    return helpers.getParameterInPipelinePromise(parameter, file.data.region, file, property);

  }))
  // Get RDS user password from parameter store
  // Add to file.data
  .pipe(data(function(file) {

    var parameter = '/csw/'+env+'/rds/user';
    var property = 'postgres_user_password';
    return helpers.getParameterInPipelinePromise(parameter, file.data.region, file, property);

  }))
  // Pass commands to psql_tunnel.py script
  .pipe(data(function(file) {

    path = config.paths.root + "/build/gulp_helpers";

    command = "CREATE DATABASE " + file.data.tool + ";";

    var promise = helpers.psqlExecuteInPipelinePromise(path, command, file)
    .then(function(output) {
        var command = "CREATE USER cloud_sec_watch WITH ENCRYPTED PASSWORD '"+file.data.postgres_user_password+"';";
        return helpers.psqlExecuteInPipelinePromise(path, command, file)
    })
    .then(function(output) {
        var command = "GRANT ALL PRIVILEGES ON DATABASE csw TO cloud_sec_watch;";
        return helpers.psqlExecuteInPipelinePromise(path, command, file)
    });

    return promise;

  }));

  return pipeline;

});

gulp.task('environment.database_switch_config', function() {
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  var config = helpers.getConfigLocations(env, tool);
  var pipeline = gulp.src(config.paths.root + "/../csw-configuration/environments/"+env+"/sql/population")
  .pipe(gulp.symlink(config.paths.root + "/build/sql"));

  return pipeline;
});

gulp.task('environment.database_run_migrations', function() {
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  var config = helpers.getConfigLocations(env, tool);
  var pipeline = gulp.src(config.files.environment_settings)
  // Parse settings into file.data
  .pipe(modifyFile(function(content, path, file) {
    var settings = JSON.parse(content);
    file.data = settings;
    return content;
  }))
  // Get RDS user password from parameter store
  // Add to file.data
  .pipe(data(function(file) {

    var parameter = '/csw/'+env+'/rds/user';
    var property = 'postgres_user_password';
    return helpers.getParameterInPipelinePromise(parameter, file.data.region, file, property);

  }))
  // Pass commands to psql_tunnel.py script
  .pipe(data(function(file) {
    var promise, path, command, meta_table;

    meta_table = "public._metadata_version";
    path = config.paths.root + "/build/gulp_helpers";

    command = "SELECT * FROM "+meta_table+";";

    promise = helpers.psqlExecuteInPipelinePromise(
        path,
        command,
        file,
        'cloud_sec_watch',
        file.data.postgres_user_password,
        'csw'
    );

    promise.then(function(output) {
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
            output = [['definition',0],['population',0]];
        }

        file.data.database = {};
        output.forEach(function(row) {
            type = row[0];
            current_level = row[1];
            file.data.database[type] = current_level;

            (function(promise, type, current_level) {
                var sqlPath, i, index;
                sqlPath = config.paths.root + "/build/sql/"+type;

                if (fs.existsSync(sqlPath)) {
                    fs.readdir(sqlPath, function(err, items) {
                      for(i=0;i<items.length;i++) {
                        item = items[i];
                        index = parseInt(item.replace(/\.sql/,''));
                        if (index > current_level) {
                            // TODO make these run sequentially so they're chained to each other rather than all
                            // chained to the parent promise.
                            (function(promise, item) {
                                promise.then(function() {
                                    var scriptPath;
                                    scriptPath = sqlPath + "/" + item;
                                    return helpers.psqlExecuteScriptInPipelinePromise(
                                        path,
                                        scriptPath,
                                        file,
                                        'cloud_sec_watch',
                                        file.data.postgres_user_password,
                                        'csw'
                                    );
                                }).then(function() {
                                    var command = "UPDATE "+meta_table+" SET version = "+index+" WHERE type='"+type+"'";
                                    return helpers.psqlExecuteInPipelinePromise(
                                        path,
                                        command,
                                        file,
                                        'cloud_sec_watch',
                                        file.data.postgres_user_password,
                                        'csw'
                                    );
                                });
                            })(promise, item);
                        }
                      }

                    });
                }
            })(promise, type, current_level);
        });
    });
    return promise;
  }));

  return pipeline;
});

gulp.task('environment.database_migrate', gulp.series(
    'environment.database_switch_config',
    'environment.database_run_migrations'
));


gulp.task('environment.database_populate', function() {

  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  var config = helpers.getConfigLocations(env, tool);

  // Load default chalice config file
  var payloads = {
    "Items": [
        {
            "Model":"Status",
            "Params":{
                "status_name": "Unknown",
                "description": "Not yet evaluated"
            }
        },
        {
            "Model":"Status",
            "Params":{
                "status_name": "Pass",
                "description": "Compliant or not-applicable"
            }
        },
        {
            "Model":"Status",
            "Params":{
                "status_name": "Fail",
                "description": "Non-compliant"
            }
        },
        {
            "Model":"CriteriaProvider",
            "Params":{
                "provider_name":"AWS Trusted Advisor"
            }
        },
        {
            "Model":"CriteriaProvider",
            "Params":{
                "provider_name":"AWS Elastic Cloud Compute (EC2) service"
            }
        },
        {
            "Model":"CriteriaProvider",
            "Params":{
                "provider_name":"AWS Identity and Access Management (IAM) service"
            }
        }
    ]
  };

  var pipeline = gulp.src(config.files.environment_settings)
  .pipe(data(function(file) {
    var i;
    var function_name = "csw-"+env+"-database_create_items";
    var output_file = config.paths.environment + "/lambda.out"
    var working = config.paths.environment;

    return helpers.lambdaInvokePromise(function_name, working, payloads, file, output_file);
  }));

  return pipeline;

});

gulp.task('environment.database_define_criteria', function() {

  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool;

  var config = helpers.getConfigLocations(env, tool);

  var pipeline = gulp.src(config.files.environment_settings)
  .pipe(data(function(file) {
    var i;
    var function_name = "csw-"+env+"-database_add_new_criteria";
    var output_file = config.paths.environment + "/lambda.out"
    var working = config.paths.environment;

    return helpers.lambdaInvokePromise(function_name, working, null, file, output_file);
  }));

  return pipeline;

});

gulp.task('environment.database_build', gulp.series(
    'environment.database_create',
    'environment.database_migrate'
));
