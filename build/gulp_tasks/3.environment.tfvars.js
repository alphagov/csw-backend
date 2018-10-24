const gulp = require('gulp');
const args = require('yargs').argv;
const data = require('gulp-data');
const modifyFile = require('gulp-modify-file');
const rename = require('gulp-rename');
const awsParamStore = require('aws-param-store');
const Input = require('prompt-input');
const helpers = require(process.cwd()+"/gulp_helpers/helpers.js");

gulp.task('environment.backend.tfvars', function() {
  var env = (args.env == undefined)?'test':args.env;
  // Load default settings
  var pipeline = gulp.src('../environments/'+env+'/settings.json')
  .pipe(modifyFile(function(content, path, file) {
    var defaults = JSON.parse(content);
    file.data = defaults;
    return content;
  }))
  .pipe(data(function(file) {
      // sanitize
      file.data.bucket = "" + file.data.bucket_name;
      file.data.key = 'staging/'+file.data.tool+'/'+file.data.environment+'.tfstate';
      file.data.encrypt = true;
      var remove = [
        'bucket_name',
        'tool',
        'google_creds',
        'host_account_id',
        'environment',
        'prefix',
        'ip_16bit_prefix',
        'ssh_key_name',
        'ssh_public_key_path'
      ];

      file.data = helpers.removePropertiesInPipeline(file.data, remove);
      return file.data
  }))
  .pipe(data(function(file) {

      var content = "";

      for (varName in file.data) {
          varValue = file.data[varName]
          switch(varValue) {
              case "true":
              case true:
              case "false":
              case false: {
                  content += varName + " = " + varValue + "\n";
              } break;
              default: {
                  content += varName + " = \"" + varValue + "\"\n";
              } break;
          }
      }

      console.log(content);
      file.data.content = content;
      return file.data;
  }))
  .pipe(modifyFile(function(content, path, file) {
      return file.data.content;
  }))
  .pipe(rename('backend.tfvars'))
  .pipe(gulp.dest(function(file) {
      var target = '../environments/'+env+'/terraform';
      console.log(target);
      return target;
  }));

  return pipeline;
});


/*
ssh_key_name = "dan"
ssh_public_key_path = "/Users/danjones/.ssh/dan.pub"
*/
gulp.task('environment.apply.tfvars', function() {
  var env = (args.env == undefined)?'test':args.env;
  // Load default settings
  var pipeline = gulp.src('../environments/'+env+'/settings.json')
  .pipe(modifyFile(function(content, path, file) {
    var defaults = JSON.parse(content);
    file.data = defaults;
    return content;
  }))
  // Get RDS root password from parameter store
  .pipe(data(function(file) {

    var parameter = '/csw/'+env+'/rds/root';
    var property = 'postgres_root_password';
    return helpers.getParameterInPipelinePromise(parameter, file.data.settings.region, file, property);

  }))
  .pipe(data(function(file) {

    // sanitize any unexpected extra paramters from AWS response
    var expected = [
      'region',
      'tool',
      'environment',
      'prefix',
      'host_account_id',
      'bucket_name',
      'postgres_root_password',
      'ip_16bit_prefix',
      'ssh_key_name',
      'ssh_public_key_path'
    ];

    file.data = helpers.removeExceptPropertiesInPipeline(file.data, expected);

    file.data.prefix = file.data.tool + '-' + file.data.environment;

    return file.data;

  }))
  .pipe(data(function(file) {

    var content = "";

    for (varName in file.data) {
      varValue = file.data[varName]
      switch(varValue) {
        case "true":
        case true:
        case "false":
        case false: {
          content += varName + " = " + varValue + "\n";
        } break;
        default: {
          content += varName + " = \"" + varValue + "\"\n";
        } break;
      }
    }

    content += 'availability_zones = ["'+file.data.region+'a","'+file.data.region+'b"]\n';

    console.log(content);
    file.data.content = content;
    return file.data;
  }))
  .pipe(modifyFile(function(content, path, file) {
      return file.data.content;
  }))
  .pipe(rename('apply.tfvars'))
  .pipe(gulp.dest(function(file) {
      var target = '../environments/'+env+'/terraform';
      console.log(target);
      return target;
  }));

  return pipeline;

});

gulp.task('environment.tfvars', gulp.series('environment.backend.tfvars','environment.apply.tfvars')); 