const gulp = require('gulp');
var modifyFile = require('gulp-modify-file');
var data = require('gulp-data');
var rename = require('gulp-rename');
var awsParamStore = require('aws-param-store');
var Input = require('prompt-input');
var args = require('yargs').argv;

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
      delete(file.data.bucket_name);
      delete(file.data.tool);
      delete(file.data.google_creds);
      delete(file.data.host_account);
      delete(file.data.environment);
      delete(file.data.prefix);
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


gulp.task('environment.apply.tfvars', function() {
  var env = (args.env == undefined)?'test':args.env;
  // Load default settings
  var pipeline = gulp.src('../environments/'+env+'/settings.json')
  .pipe(modifyFile(function(content, path, file) {
    var defaults = JSON.parse(content);
    file.data = defaults;
    return content;
  }))
  // Get Google API Console OAuth credentials file from AWS SSM Parameter Store 
  .pipe(data(function(file) {

    var promise = awsParamStore.getParameter( '/csw/'+env+'/rds/root', { region: file.data.region })

    promise.then(function(parameter) {
      file.data.root = parameter.Value;
      return file.data;
    });

    return promise;
  }))
  .pipe(data(function(file) {

    // sanitize any unexpected extra paramters from AWS response
    var expected = [
      'region',
      'tool',
      'environment',
      'prefix',
      'host_account',
      'bucket_name'
    ];

    for (item in file.data) {
      if (expected.indexOf(item) < 0) {
        delete file.data[item];
      }
    }
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