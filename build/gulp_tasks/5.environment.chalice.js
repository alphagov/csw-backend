var gulp = require('gulp');
var data = require('gulp-data');
var args = require('yargs').argv;
const util = require('util');
const exec = util.promisify(require('child_process').exec);

/*
BUILD THIS
{
  "version": "2.0",
  "app_name": "yyy",
  "stages": {
    "zzz": {
      "api_gateway_stage": "app",
      "manage_iam_role": false,
      "iam_role_arn": "arn:aws:iam::xxx:role/yyy-zzz_CstSecurityAgentRole",
      "environment_variables": {
        "CSW_ENV": "csw-dan",
        "CSW_USER": "cloud_sec_watch",
        "CSW_PASSWORD": "xxx",
        "CSW_HOST": "xxx",
        "CSW_PORT": "5432"
      },
      "subnet_ids": ["xxx1","xxx2"],
      "security_group_ids": ["xxx3"]
    }
  }
}
*/
gulp.task('environment.chalice_config', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var root_path = __dirname;
  var dirs = root_path.split('/');
  dirs.pop();
  dirs.pop();
  root_path = dirs.join('/');

  var terraform_path = root_path + '/environments/'+env+'/terraform';
  var settings_file = root_path + '/environments/'+env+'/settings.json';
  var tool_path = '/csw-infra/tools/'+tool;
  // Load default settings
  var pipeline = gulp.src(settings_file)
  .pipe(gulp.symlink(terraform_path))
  .pipe(data(function(file) {

    var promise = exec('terraform output -json', { cwd: terraform_path+tool_path })
    .then(
      function(out) {
        console.log("SUCCESS");
        console.log(out);
        file.data = JSON.parse(out.stdout);
        return file.data;
      }, 
      function(err) {
        console.log("FAILURE");
        console.log(err);
        return file.data;
      }
    );

    return promise;
  }))
  .pipe(data(function(file) {
    console.log(file.data);
  }));

  return pipeline;
});
