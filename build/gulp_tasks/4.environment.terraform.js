var gulp = require('gulp');
var data = require('gulp-data');
var args = require('yargs').argv;
const util = require('util');
const exec = util.promisify(require('child_process').exec);

gulp.task('environment.terraform_setup', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var root_path = __dirname;
  var dirs = root_path.split('/');
  dirs.pop();
  dirs.pop();
  root_path = dirs.join('/');

  var terraform_path = root_path + '/environments/'+env+'/terraform';
  var tool_path = '/csw-infra/tools/'+tool;
  // Load default settings
  var pipeline = gulp.src('./node_modules/csw-infra')
  .pipe(gulp.symlink(terraform_path))
  .pipe(data(function(file) {
  	return exec('terraform init -backend-config='+terraform_path+'/backend.tfvars -reconfigure', { cwd: terraform_path+tool_path })
    .then(
      function(out) {
        console.log("SUCCESS");
        console.log(out.stdout);
        return file.data;
      }, 
      function(err) {
        console.log("FAILURE");
        console.log(err);
        return file.data;
      }
    );
  }))
  .pipe(data(function(file) {
  	return exec('terraform plan -var-file='+terraform_path+'/apply.tfvars', { cwd: terraform_path+tool_path })
    .then(
      function(out) {
        console.log("SUCCESS");
        console.log(out.stdout);
        return file.data;
      }, 
      function(err) {
        console.log("FAILURE");
        console.log(err);
        return file.data;
      }
    );
  }));

  return pipeline;
});

gulp.task('environment.terraform_apply', function() {
  
  var env = (args.env == undefined)?'test':args.env;
  var tool = (args.tool == undefined)?'csw':args.tool; 
  
  var root_path = __dirname;
  var dirs = root_path.split('/');
  dirs.pop();
  dirs.pop();
  root_path = dirs.join('/');

  var terraform_path = root_path + '/environments/'+env+'/terraform';
  var tool_path = '/csw-infra/tools/'+tool;
  // Load default settings
  var pipeline = gulp.src('./node_modules/csw-infra')
  .pipe(gulp.symlink(terraform_path))
  .pipe(data(function(file) {
  	return exec('terraform apply -var-file='+terraform_path+'/apply.tfvars', { cwd: terraform_path+tool_path })
  	.then(
      function(out) {
        console.log("SUCCESS");
        console.log(out.stdout);
        return file.data;
      }, 
      function(err) {
        console.log("FAILURE");
        console.log(err);
        return file.data;
      }
    );
  }));
  return pipeline;
});

gulp.task('environment.terraform', gulp.series('environment.terraform_setup','environment.terraform_apply'));